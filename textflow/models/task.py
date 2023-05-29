"""Task model.

This module contains the Task model.

Classes
-------
Task
"""
import dataclasses
import logging
import typing

import pydantic

from textflow.database import db

logger = logging.getLogger(__name__)

__all__ = [
    'Task',
]


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class Task(db.ModelMixin):
    """Task Entity. Contains labels and condition.

    Attributes
    ----------
    id : int
        Primary key.
    title : str
        Title of task.
    description : str
        Description of task.
    type : str
        Type of task.
    project_id : int
        Project id of task.
    order : int
        Order of task.
    labels : list of Label
        Labels of task.
    condition : dict
        Condition of task.
    """
    __table__ = db.Table(
        'task',
        db.mapper_registry.metadata,
        db.Column('id', db.Integer, primary_key=True, autoincrement=True),
        db.Column('title', db.String(80), default=None, nullable=True),
        db.Column('description', db.Text, default=None, nullable=True),
        db.Column('type', db.String(80), nullable=False),
        db.Column('order', db.Integer, default=1),
        db.Column('condition', db.JSON, nullable=True),
        db.Column('project_id', db.Integer, db.ForeignKey('project.id'),
                  nullable=False),
    )

    __mapper_args__ = {
        'properties': dict(
            labels=db.relationship(
                'Label', backref='task', lazy=True,
                cascade='all, delete', order_by='Label.order'
            )
        )
    }

    project_id: int = pydantic.Field()
    type: str = pydantic.Field()
    title: typing.Optional[str] = pydantic.Field(default=None)
    description: typing.Optional[str] = pydantic.Field(
        default=None)
    order: typing.Optional[int] = pydantic.Field(default=1)
    condition: typing.Optional[pydantic.Json[typing.Any]] = \
        pydantic.Field(default=None)
    id: typing.Optional[int] = pydantic.Field(default=None)
