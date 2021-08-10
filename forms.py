from flask import g
from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, TextAreaField, BooleanField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError, InputRequired, Optional
from models import User

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

class UserAddForm(FlaskForm):
    """Form for adding users"""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', choices =[(s,s) for s in states])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class EditProfileForm(FlaskForm):
    """Form for adding users"""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', choices =[(s,s) for s in states])
    password = PasswordField('Password', validators=[Length(min=6)])

    def validate_username(self, username):
        if username.data != g.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != g.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UpdatePhoto(FlaskForm):
    """Form for adding users"""

    image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png']), FileRequired()])


class GameForm(FlaskForm):
    """Form for creating a game"""

    title = StringField('Title', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    address = StringField('Address')
    city = StringField('City', validators=[InputRequired()])
    state = SelectField('State', choices =[(s,s) for s in states])
    date = DateField('PUG Date', format='%Y-%m-%d', validators=[InputRequired()])
    time = TimeField('PUG Time', validators=[InputRequired()])

class EditGameForm(FlaskForm):
    """Form for creating a game"""

    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    address = StringField('Address')
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', choices =[(s,s) for s in states])
    date = DateField('PUG Date', format='%Y-%m-%d', validators=[InputRequired()])
    time = TimeField('PUG Time', validators=[InputRequired()])

    password = PasswordField('Password', validators=[Length(min=6)])

class AddMessage(FlaskForm):
    """form for creating a message"""

    text = TextAreaField('add a message', validators = [InputRequired()])

class FindCourtForm(FlaskForm):
    """form for finding a court"""

    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', choices =[(s,s) for s in states])

class FindGame(FlaskForm):
    """form for finding a game"""

    city = StringField('City', validators=[Optional()])
    state = SelectField('State', choices =[(s,s) for s in states])

class InviteFriendsForm(FlaskForm):

    message = StringField('Message')
    friend = BooleanField('friend', default=False)


