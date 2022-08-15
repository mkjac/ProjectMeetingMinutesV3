from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import *


class RegistrationForm(FlaskForm):
    username = StringField('username_label', validators=[InputRequired(message="Username Required"), Length(
        min=3, max=50, message="Username must be between 3 and 50 characters")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password Required"), Length(
        min=3, max=50, message="Password must be between 3 and 50 characters")])
    confirm_pw = PasswordField('confirm_pw_label', validators=[InputRequired(
        message="Confirm password required"), EqualTo('password', message="Passwords must match")])
    register_button = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('username_label', validators=[
        InputRequired(message="Username required")])
    password = PasswordField('password_label', validators=[
        InputRequired(message="Password required")])
    login_button = SubmitField('Login')


class ActionsForm(FlaskForm):
    action = TextAreaField('action_label', validators=[
        InputRequired(message="Action required")])
    actionedBy = TextAreaField('actionedBy_label', validators=[
        InputRequired(message="Actioned By required")])


class NewForm(FlaskForm):
    """ User Home Form """
    date = DateField('date_label', validators=[
        InputRequired(message="Date required")])
    time = TimeField('time_label', validators=[
        InputRequired(message="Time required")])
    attendees = TextAreaField('attendees_label', validators=[
        InputRequired(message="Attendees required")])
    absentees = TextAreaField('absentees_label')
    agenda = TextAreaField('agenda_label', validators=[
        InputRequired(message="Agenda required")])
    # actions = FieldList(FormField(ActionsForm), min_entries=1)
    extraInfo = TextAreaField('extraInfo_label')
    files = FileField('files_label')
    add_minutes_button = SubmitField('Add Minutes')
