"""BackgroundJob entity.

This module contains the BackgroundJob entity which is used to keep track of
background jobs that are running

Classes
-------
BackgroundJob
"""
import dataclasses
import typing

import pydantic

from textflow.database import db

__all__ = [
    'BackgroundJob',
]


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class BackgroundJob(db.ModelMixin):
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
    __table__ = db.Table(
        'background_job',
        db.mapper_registry.metadata,
        db.Column('id', db.String(128), primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                  nullable=False),
        db.Column('project_id', db.Integer, db.ForeignKey('project.id'),
                  nullable=True),
        db.Column('hash', db.String(512), nullable=True),
    )

    # task id is a unique id of the task that is running (e.g., from celery)
    id: int = pydantic.Field()
    # user id of the user who started the task is stored here to keep track of
    # who started the task (todo: and who can cancel it)
    user_id: int = pydantic.Field()
    # project id of the project that the task is related to
    project_id: typing.Optional[int] = pydantic.Field(
        default=None
    )
    # hash of a task is the hash of the task's parameters so that we can
    # identify if a task with the same parameters has already been run
    # (or is running) and avoid running it again simultaneously
    # for example you dont want to delete the documents of a project twice at
    # the same time by same or two users
    hash: typing.Optional[str] = pydantic.Field(
        default=None
    )
