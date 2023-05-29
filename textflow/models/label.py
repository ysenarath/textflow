"""Label model.

This module contains the Label model.

Classes
-------
Label
"""
import dataclasses
import typing

import pydantic

from sqlalchemy import CheckConstraint

from textflow.database import db

__all__ = [
    'Label',
]


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class Label(db.ModelMixin):
    """Label Entity - contains label information"""
    __table__ = db.Table(
        'label',
        db.mapper_registry.metadata,
        db.Column('id', db.Integer, primary_key=True, autoincrement=True),
        db.Column('task_id', db.Integer,
                  db.ForeignKey('task.id', ondelete="CASCADE"),
                  nullable=False),
        db.Column('value', db.String(50), nullable=False),
        db.Column('label', db.String(50), nullable=False),
        db.Column('order', db.Integer, nullable=False),
        db.Column('color', db.String(9), CheckConstraint(
            "color LIKE '#______%'"), nullable=True),
        db.Column('group', db.String(50), nullable=True),
    )

    task_id: int = pydantic.Field()
    # add regex constraint to value
    value: str = pydantic.Field()
    label: typing.Optional[str] = pydantic.Field(default='Label')
    order: typing.Optional[int] = pydantic.Field(default=1)
    # add regex constraint to color
    color: typing.Optional[str] = pydantic.Field(default=None)
    # add regex constraint to group
    # Regex: [^A-Za-z0-9_-]
    group: typing.Optional[str] = pydantic.Field(default=None)
    id: typing.Optional[int] = pydantic.Field(default=None)
