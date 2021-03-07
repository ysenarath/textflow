from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, BooleanField
from wtforms.validators import DataRequired

__all__ = [
    'LabelsForm',
    'LabelForm'
]


class LabelForm(FlaskForm):
    selected = BooleanField('selected')
    id = StringField('ID')
    label = StringField('Label', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])


class LabelsForm(FlaskForm):
    labels = FieldList(FormField(LabelForm))
