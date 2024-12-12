from flask import render_template, redirect, url_for, request, flash, abort, jsonify
from app import app, db
from app.models import Event, User, user_event
from app.forms import CreateEventForm, SearchForm, LoginForm, SignUpForm
from flask_login import current_user, login_required, login_user, logout_user
import datetime

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('homepage'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already taken', 'danger')
            return redirect(url_for('signup'))
        
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('sign_up.html', form=form)

@app.route('/homepage')
@login_required
def homepage():
    # Find events the user is attending but haven't passed
    attending_events = (
        Event.query.join(user_event)
        .filter(user_event.c.user_id == current_user.id, Event.date >= datetime.date.today())
        .all()
    )

    # Find upcoming events the user is managing
    upcoming_managed_events = (
        Event.query.filter_by(organizer=current_user.username)
        .filter(Event.date >= datetime.date.today())
        .all()
    )

    # Find past events the user is managing
    past_managed_events = (
        Event.query.filter_by(organizer=current_user.username)
        .filter(Event.date < datetime.date.today())
        .all()
    )

    # Find events the user has attended
    attended_events = (
        Event.query.join(user_event)
        .filter(user_event.c.user_id == current_user.id, Event.date < datetime.date.today())
        .all()
    )

    return render_template(
        'homepage.html',
        attending_events=attending_events,
        upcoming_managed_events=upcoming_managed_events,
        past_managed_events=past_managed_events,
        attended_events=attended_events,
    )

@app.route('/search-event', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    sort_by = request.args.get('sort_by', 'alphabetical')
    today = datetime.date.today()
    query = Event.query.filter(
        ~Event.users.any(User.id == current_user.id),
        Event.date >= today
    )

    if form.validate_on_submit() and form.query.data:
        search_query = form.query.data
        query = query.filter(
            (Event.title.ilike(f'%{search_query}%') |
             Event.description.ilike(f'%{search_query}%') |
             Event.location.ilike(f'%{search_query}%'))
        )

    # Apply sorting
    if sort_by == 'alphabetical':
        query = query.order_by(Event.title)
    elif sort_by == 'rating':
        query = query.order_by(Event.organizer.rating)
    elif sort_by == 'attendance':
        results = query.all()
        results = sorted(results, key=lambda e: len(e.users), reverse=True)
        return render_template('search.html', form=form, results=results, sort_by=sort_by)

    results = query.all()
    return render_template('search.html', form=form, results=results, sort_by=sort_by)


@app.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = CreateEventForm()
    if form.validate_on_submit():
        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            organizer=current_user.username
        )
        db.session.add(new_event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('homepage'))
    
    return render_template('create_event.html', form=form)



@app.route('/event-attendees/<int:event_id>')
@login_required
def event_attendees(event_id):
    event = Event.query.get_or_404(event_id)

    if event.organizer != current_user.username:
        flash('You are not authorized to view attendees for this event.', 'danger')
        return redirect(url_for('homepage'))

    attendees = User.query.join(user_event).filter(user_event.c.event_id == event_id).all()

    return render_template('event_attendees.html', event=event, attendees=attendees)

@app.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.organizer != current_user.username:
        flash('You are not authorized to edit this event.', 'danger')
        return redirect(url_for('homepage'))

    form = CreateEventForm(obj=event)

    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.time = form.time.data
        event.location = form.location.data

        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('homepage'))

    return render_template('edit_event.html', form=form, event=event)

@app.route('/stop-attending/<int:event_id>', methods=['POST'])
@login_required
def stop_attending(event_id):
    event = Event.query.get_or_404(event_id)
    
    this_event = db.session.query(user_event).filter_by(user_id=current_user.id, event_id=event.id).first()

    if this_event:
        db.session.execute(
            user_event.delete().where(
                user_event.c.user_id == current_user.id, 
                user_event.c.event_id == event_id
            )
        )
        db.session.commit()
        flash('You have stopped attending the event.', 'success')
    else:
        flash('You are not attending this event.', 'danger')

    return redirect(url_for('homepage'))

@app.route('/attend-event/<int:event_id>', methods=['POST'])
@login_required
def attend_event(event_id):
    event = Event.query.get_or_404(event_id)

    existing_attendance = db.session.query(user_event).filter_by(user_id=current_user.id, event_id=event.id).first()
    if not existing_attendance:
        db.session.execute(user_event.insert().values(user_id=current_user.id, event_id=event.id))
        db.session.commit()
        flash('You are now attending the event.', 'success')
    else:
        flash('You are already attending this event.', 'info')
    
    return redirect(url_for('search'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('homepage'))

@app.route('/rate', methods=['POST'])
@login_required
def rate_post():
    data = request.get_json()
    action = data.get('action')
    post_id = data.get('post_id')

    if not post_id or not action:
        return jsonify({'error': 'Invalid request'}), 400

    post = Event.query.get(post_id)
    if not post:
        return jsonify({'error': 'Event not found'}), 404

    if action == 'LIKE':
        post.likes += 1
    elif action == 'DISLIKE':
        post.dislikes += 1
    else:
        return jsonify({'error': 'Invalid action'}), 400

    db.session.commit()
    return jsonify({'message': f'You {action.lower()}d the event.'})
