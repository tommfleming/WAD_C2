from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, PasswordField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import datetime

class CreateEventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Create Event')

    def validate_date(self, field):
        if field.data < datetime.date.today():
            raise ValidationError("This date has already passed")

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Log In')

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25, message="Username must be between 3 and 25 characters.")])
    email = StringField('Email', validators=[DataRequired(), Email(message="Enter a valid email address.")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters long.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Sign Up')