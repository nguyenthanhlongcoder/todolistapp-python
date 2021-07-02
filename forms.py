from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired

class SignUpForm(FlaskForm):
    inputFirstName = StringField('First Name',
                                 [DataRequired(message="Pleas enter your first name!")])
    inputLastName = StringField('Last Name',
                                [DataRequired(message="Pleas enter your last name!")])
    inputEmail = StringField('Email address',
                             [Email(message="Not a valid email address!"),
                              DataRequired(message="Please enter your email address!")])
    inputPassword = PasswordField('Password',
                                  [InputRequired(message="Please enter your password"),
                                   EqualTo('inputConfirmPassword', message="Password doesnt match!")])
    inputConfirmPassword = PasswordField('Confirm password')
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    inputEmail = StringField('Email address', [Email(message='Not a valid email address!!'), DataRequired(message='Please enter your email address!!')])
    inputPassword = PasswordField('Password', [InputRequired(message='Please enter your password')])
    submit = SubmitField('Sign In')

class TaskForm(FlaskForm):
    inputTask = StringField('Task', [DataRequired(message="Please enter the task!")])
    submit = SubmitField('Add Task')

class PriotiryForm(FlaskForm):
    inputTask = StringField('Priority', [DataRequired(message="Please enter the priority!")])
    submit = SubmitField('Add Priority')
