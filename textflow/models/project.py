"""Project model.

This module contains the Project model.

Classes
-------
Project
"""
import logging

import sqlalchemy as sa

from textflow.models.base import mapper_registry, ModelMixin

__all__ = [
    'Project',
]

logger = logging.getLogger(__name__)


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class Project(ModelMixin):
    """This model contains the project information.

    Attributes
    ----------
    id : int
        Primary key.
    name : str
        Name of project.
    description : str
        Description of project.
    documents : list of Document
        Documents of project.
    users : list of Assignment
        Users of project.
    redundancy : int
        Redundancy of number of annotations per document user.
    guideline_template : str
        Template for guideline.
    jobs : list of BackgroundJob
        Background jobs related to this project.
    tasks : list of Task
        Tasks of project (ordedred by Task.order).
    """
    __table__ = sa.Table(
        'project',
        mapper_registry.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(80), nullable=False),
        sa.Column('description', sa.Text,
                  default='Description is not available.'),
        sa.Column('redundancy', sa.Integer, default=3, nullable=True),
        sa.Column('guideline', sa.Text, default=None, nullable=True),
    )

    __mapper_args__ = {
        'properties': dict(
            documents=sa.orm.relationship('Document', backref='project'),
            assignments=sa.orm.relationship('Assignment', backref='project',
                                            lazy=True, cascade='all, delete'),
            tasks=sa.orm.relationship('Task', backref='project', lazy=True,
                                      order_by='Task.order'),
        )
    }
