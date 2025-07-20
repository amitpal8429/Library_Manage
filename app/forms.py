from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    time = StringField('Time Slot', validators=[InputRequired()])
    capacity = IntegerField('Capacity', validators=[InputRequired()])
    submit = SubmitField('Create Event')
