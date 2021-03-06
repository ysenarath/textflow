from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

__all__ = [
    'ProjectForm'
]


class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
