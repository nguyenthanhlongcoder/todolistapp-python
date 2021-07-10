from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired
from wtforms.fields.core import SelectField
from wtforms.fields.html5 import DateField
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
    inputTaskDeadline = DateField('Task Deadline', format='%Y-%m-%d')
    submit = SubmitField('Add Task')

class PriotiryForm(FlaskForm):
    inputTask = StringField('Priority', [DataRequired(message="Please enter the priority!")])
    submit = SubmitField('Add Priority')

class ProjectForm(FlaskForm):
    inputProjectName = StringField('Project Name',
        [DataRequired(message="Please enter your project name!")])
    inputProjectDesc = TextAreaField('Project Description')

    inputProjectDeadline = DateField('Project Deadline', format='%Y-%m-%d')
    submit = SubmitField('Add/Update Project')


