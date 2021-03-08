from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange

__all__ = [
    'ProjectForm'
]

project_types = [
    ('sequence_labeling', 'Sequence Labeling'),
    ('document_classification', 'Document Classification'),
]


class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], choices=project_types)
    redundancy = IntegerField('Redundancy', validators=[DataRequired(), NumberRange(min=1)])
    guideline_template = TextAreaField('Guideline', validators=[DataRequired()])
