from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, BooleanField, SelectField
from wtforms.validators import DataRequired

__all__ = [
    'UsersForm',
    'AssignmentForm'
]

project_user_roles = [
    ('default', 'Default'),
    ('manager', 'Manager'),
    ('admin', 'Administer'),
]


class UserForm(FlaskForm):
    id = StringField('ID')
    username = StringField('Username', validators=[DataRequired()])


class AssignmentForm(FlaskForm):
    selected = BooleanField('selected')
    user = FormField(UserForm)
    role = SelectField('Role', validators=[DataRequired()], choices=project_user_roles)


class UsersForm(FlaskForm):
    users = FieldList(FormField(AssignmentForm))
