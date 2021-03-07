from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

__all__ = [
    'LoginForm'
]


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=8, max=25)])
