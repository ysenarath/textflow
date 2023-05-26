"""Label model.

This module contains the Label model.

Classes
-------
Label
"""
import random
import re

from sqlalchemy import CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from PIL import ImageColor

from textflow.database import db

__all__ = [
    'Label',
]

# TODO: move to config
DEFAULT_LABEL_COLOR = '#FFA500'


class Label(db.Model):
    """Label Entity - contains label information"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _value = db.Column('value', db.String(50), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, default=1)
    _color = db.Column('color', db.String(9), CheckConstraint(
        "color LIKE '#______%'"), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey(
        'task.id', ondelete="CASCADE"), nullable=False)
    _group = db.Column('group', db.String(50), nullable=True)

    def __init__(self, **kwargs):
        """Create a new Label.

        Parameters
        ----------
        **kwargs
            Arbitrary keyword arguments.
        """
        if '_color' in kwargs:
            kwargs['color'] = kwargs.pop('_color')
        color = kwargs.pop('color', None)
        super(Label, self).__init__(**kwargs)
        self.color = color

    @hybrid_property
    def group(self):
        """Get the group of the label.

        Returns
        -------
        str
            Group of the label.
        """
        return self._group

    @group.setter
    def group(self, value):
        """Set the group of the label.

        Parameters
        ----------
        value : str
            Group of the label.
        """
        if value is not None:
            value = str(value).strip()
        if value == '':
            value = None
        elif value is not None:
            value = re.sub(r'[^A-Za-z0-9_-]', '_', value)
        self._group = value

    @hybrid_property
    def value(self):
        """Get the value of the label.

        Returns
        -------
        str
            Value of the label.
        """
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the label.

        Parameters
        ----------
        value : str
            Value of the label.
        """
        value = str(value)
        self._value = re.sub(r'[^A-Za-z0-9_-]', '_', value)

    @hybrid_property
    def color(self):
        """Get the color of the label.

        Returns
        -------
        str
            Color of the label.
        """
        color = self._color
        if color is None:
            color = DEFAULT_LABEL_COLOR
        return color

    @color.setter
    def color(self, value):
        """Set the color of the label.

        Parameters
        ----------
        value : str
            Color of the label.

        Raises
        ------
        ValueError
            If the color value is invalid.

        Notes
        -----
        The color can be set using the following values:
        - None: default highlight color (gray)
        - 'none': default highlight color (gray)
        - 'random': random color
        - '#RRGGBB': hex color
        - '#RRGGBBAA': hex color with alpha channel
        - 'rgb(R, G, B)': rgb color
        - 'rgba(R, G, B, A)': rgba color
        - 'color_name': color name

        Examples
        --------
        >>> label.color = None
        >>> label.color = 'none'
        >>> label.color = 'random'
        >>> label.color = '#FFA500'
        >>> label.color = '#FFA500FF'
        >>> label.color = 'rgb(255, 165, 0)'
        >>> label.color = 'rgba(255, 165, 0, 255)'
        >>> label.color = 'orange'
        """
        is_none = isinstance(value, str) and value.lower() == 'none'
        if value is None or is_none:
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
            except ValueError:
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
        """Get the contrast color of the label.

        Returns
        -------
        str
            Contrast color of the label.
        """
        color = 0xffffff-int(self.color.lstrip('#'), 16)
        return f'#{color:06X}'

    @property
    def color_rgb(self):
        """Get the color of the label as rgb string.

        Returns
        -------
        str
            Color of the label as rgb string.
        """
        color = self.color
        if color is None:
            color = DEFAULT_LABEL_COLOR
        rgb = ImageColor.getrgb(color)
        return '{},{},{}'.format(*rgb[:3])

    def to_dict(self):
        """Convert to dictionary.

        Returns
        -------
        dict
            Dictionary representation of Label.
        """
        return {
            'id': self.id,
            'label': self.label,
            'value': self.value,
            'order': self.order,
            'color': self.color,
            'group': self.group,
            'task_id': self.task_id,
        }
