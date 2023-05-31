"""Label schema.

Classes
-------
Label
"""
import typing

import pydantic

from textflow.schemas.base import Schema

__all__ = [
    'Label',
]


class Label(Schema):
    task_id: int = pydantic.Field()
    # add regex constraint to value
    value: str = pydantic.Field()
    label: typing.Optional[str] = pydantic.Field(default='Label')
    order: typing.Optional[int] = pydantic.Field(default=1)
    # add regex constraint to color
    color: typing.Optional[str] = pydantic.Field(default=None)
    # add regex constraint to group
    # Regex: [^A-Za-z0-9_-]
    group: typing.Optional[str] = pydantic.Field(default=None)
    id: typing.Optional[int] = pydantic.Field(default=None)
