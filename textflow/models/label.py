"""Label model.

This module contains the Label model.

Classes
-------
Label
"""
import sqlalchemy as sa
from sqlalchemy import CheckConstraint

from textflow.models.base import mapper_registry, ModelMixin


__all__ = [
    'Label',
]


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class Label(ModelMixin):
    """Label Entity - contains label information"""
    __table__ = sa.Table(
        'label',
        mapper_registry.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Integer,
                  sa.ForeignKey('task.id', ondelete="CASCADE"),
                  nullable=False),
        sa.Column('value', sa.String(50), nullable=False),
        sa.Column('label', sa.String(50), nullable=False),
        sa.Column('order', sa.Integer, nullable=False),
        sa.Column('color', sa.String(9), CheckConstraint(
            "color LIKE '#______%'"), nullable=True),
        sa.Column('group', sa.String(50), nullable=True),
    )
