"""Task schema.

Classes
-------
Task
"""
import logging
import typing

import pydantic

from textflow.schemas.base import Schema


logger = logging.getLogger(__name__)

__all__ = [
    'Task',
]


class Task(Schema):
    project_id: int = pydantic.Field()
    type: str = pydantic.Field()
    title: typing.Optional[str] = pydantic.Field(default=None)
    description: typing.Optional[str] = pydantic.Field(
        default=None)
    order: typing.Optional[int] = pydantic.Field(default=1)
    condition: typing.Optional[pydantic.Json[typing.Any]] = \
        pydantic.Field(default=None)
    id: typing.Optional[int] = pydantic.Field(default=None)
