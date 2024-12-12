from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Intermediary table to facilitate many-many relationship between User and Event
user_event = db.Table('user_event',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    rating = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    organizer = db.Column(db.String(50), nullable=False)
    liked = db.Column(db.Integer, default=0)
    disliked = db.Column(db.Integer, default=0)

    users = db.relationship('User', secondary='user_event', backref='events')

    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, organizer={self.organizer})>"
