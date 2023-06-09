"""Task schema.

Classes
-------
Task
TaskBase
"""
import json
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
    condition: typing.Optional[str] = \
        pydantic.Field(default=None)

    @pydantic.validator('condition')
    def condition_must_be_json_or_empty(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        if len(v) == 0:
            return None
        try:
            v = json.loads(v)
        except json.JSONDecodeError:
            raise ValueError('Invalid JSON')
        return json.dumps(v)


class Task(TaskBase):
    project_id: int = pydantic.Field()
    id: typing.Optional[int] = pydantic.Field(default=None)
