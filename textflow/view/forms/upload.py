from flask_wtf import FlaskForm
from wtforms import FileField

__all__ = [
    'UploadForm',
]


class UploadForm(FlaskForm):
    file = FileField()
