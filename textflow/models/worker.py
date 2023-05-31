"""BackgroundJob entity.

This module contains the BackgroundJob entity which is used to keep track of
background jobs that are running

Classes
-------
BackgroundJob
"""
import sqlalchemy as sa

from textflow.models.base import mapper_registry, ModelMixin

__all__ = [
    'BackgroundJob',
]


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class BackgroundJob(ModelMixin):
    """BackgroundJob Entity.

    This entity is used to keep track of background jobs that are running.

    Attributes
    ----------
    id : str
        Unique id of the task that is running (e.g., from celery).
    user_id : int
        User id of the user who started the task is stored here to keep track 
        of who started the task (todo: and who can cancel it)
    project_id : int
        Project id of the project that the task is related to.
    hash : str
        Hash of a task is the hash of the task's parameters so that we can
        identify if a task with the same parameters has already been run
        (or is running) and avoid running it again simultaneously.
    """
    __table__ = sa.Table(
        'background_job',
        mapper_registry.metadata,
        sa.Column('id', sa.String(128), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'),
                  nullable=False),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id'),
                  nullable=True),
        sa.Column('hash', sa.String(512), nullable=True),
    )
