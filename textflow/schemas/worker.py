"""BackgroundJob schema.

Classes
-------
BackgroundJob
"""
import typing

import pydantic

from textflow.schemas.base import Schema

__all__ = [
    'BackgroundJob',
]


class BackgroundJob(Schema):
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
