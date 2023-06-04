"""Task schema.

Classes
-------
Task
TaskBase
"""
import logging
import typing

import pydantic

from textflow.schemas.base import Schema


logger = logging.getLogger(__name__)

__all__ = [
    'Task',
    'TaskBase',
]


class TaskBase(Schema):
    type: str = pydantic.Field()
    title: typing.Optional[str] = pydantic.Field(default=None)
    description: typing.Optional[str] = pydantic.Field(
        default=None)
    order: typing.Optional[int] = pydantic.Field(default=1)
    condition: typing.Optional[pydantic.Json[typing.Any]] = \
        pydantic.Field(default=None)


class Task(TaskBase):
    project_id: int = pydantic.Field()
    id: typing.Optional[int] = pydantic.Field(default=None)
