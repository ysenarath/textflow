""" Label Entity """
import random
import re

from sqlalchemy import CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from PIL import ImageColor

from textflow.services.base import database as db

DEFAULT_LABEL_COLOR = '#FFA500'


class Label(db.Model):
    """Label Entity - contains label information"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _value = db.Column('value', db.String(50), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, default=1)
    _color = db.Column('color', db.String(9), CheckConstraint(
        "color LIKE '#______%'"), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id', ondelete="CASCADE"), nullable=False)

    def __init__(self, **kwargs):
        if '_color' in kwargs:
            kwargs['color'] = kwargs.pop('_color')
        color = kwargs.pop('color', None)
        super(Label, self).__init__(**kwargs)
        self.color = color

    @hybrid_property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        value = str(value)
        self._value = re.sub(r'[^A-Za-z0-9_-]', '_', value)

    @hybrid_property
    def color(self):
        """Get the color of the label

        :return: color of the label
        """
        color = self._color
        if color is None:
            color = DEFAULT_LABEL_COLOR
        return color

    @color.setter
    def color(self, value):
        """Set the color of the label

        :param value: color value
        :return: None
        """
        if value is None or (isinstance(value, str) and value.lower() == 'none'):
            # set color to None => default highlight color (gray)
            hex_value = None
        elif isinstance(value, str) and value.lower() == 'random':
            # generate random color using random module
            value = random.randint(0, 0xffffff)
            hex_value = f'#{value:06X}'
        else:
            # get the rgba value from the color name
            try:
                rgb_value = ImageColor.getrgb(value)
            except ValueError as ex:
                # on unknown color default to None
                hex_value = None
            else:
                # convert to hex value
                if len(rgb_value) == 3:
                    hex_value = '#{:02x}{:02x}{:02x}'.format(*rgb_value)
                elif len(rgb_value) == 4:
                    hex_value = '#{:02x}{:02x}{:02x}{:02x}'.format(*rgb_value)
                else:
                    raise ValueError('Invalid color value')
        self._color = hex_value

    @property
    def contrast_color(self):
        """Get the contrast color of the label"""
        color = 0xffffff-int(self.color, 16)
        return f'#{color:06X}'

    @property
    def color_rgb(self):
        color = self.color
        if color is None:
            color = DEFAULT_LABEL_COLOR
        rgb = ImageColor.getrgb(color)
        return '{},{},{}'.format(*rgb[:3])
