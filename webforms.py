from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length




#create user form with email
class AddUserform(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email(message='Enter a valid email')])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords Must Match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit= SubmitField("Submit")

#create user form with email
class UpdateUser(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    name = StringField("Name:", validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email(message='Enter a valid email')])
    submit= SubmitField("Submit")


#create a login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


#chatbot form
class Chatform(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    submit = SubmitField('Submit')
    