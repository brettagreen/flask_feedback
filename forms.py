from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length

class AddUserForm(FlaskForm):
    """Form for adding/registering a new user."""
    
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])

class AddLoginForm(FlaskForm):
    """Form for handling user login"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class AddFeedbackForm(FlaskForm):
    """Form for entering feedback"""
    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = StringField("Content", validators=[InputRequired()])

class PasswordResetRequestForm(FlaskForm):
    """Form to request pw reset"""
    email = EmailField("Email", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])

class PasswordResetForm(FlaskForm):
    password1 = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Re-enter your password", validators=[InputRequired()])