from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, BooleanField, SelectField
from wtforms.validators import DataRequired

__all__ = [
    'UsersForm',
    'AssignmentForm'
]


class UserForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])


class AssignmentForm(FlaskForm):
    selected = BooleanField('selected')
    user = FormField(UserForm)
    role = StringField('Role', validators=[DataRequired()])


class UsersForm(FlaskForm):
    users = FieldList(FormField(AssignmentForm))
