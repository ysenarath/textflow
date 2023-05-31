"""Task model.

This module contains the Task model.

Classes
-------
Task
"""
import logging

import sqlalchemy as sa

from textflow.models.base import mapper_registry, ModelMixin


logger = logging.getLogger(__name__)

__all__ = [
    'Task',
]


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class Task(ModelMixin):
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
    __table__ = sa.Table(
        'task',
        mapper_registry.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(80), default=None, nullable=True),
        sa.Column('description', sa.Text, default=None, nullable=True),
        sa.Column('type', sa.String(80), nullable=False),
        sa.Column('order', sa.Integer, default=1),
        sa.Column('condition', sa.JSON, nullable=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id'),
                  nullable=False),
    )

    __mapper_args__ = {
        'properties': dict(
            labels=sa.orm.relationship(
                'Label', backref='task', lazy=True,
                cascade='all, delete', order_by='Label.order'
            )
        )
    }
