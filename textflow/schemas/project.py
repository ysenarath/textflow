"""Project schema.

Classes
-------
Project
"""
import logging
import typing

import pydantic

from textflow.schemas.base import Schema


__all__ = [
    'ProjectBase',
    'Project',
]

logger = logging.getLogger(__name__)


class ProjectBase(Schema):
    name: str = pydantic.Field(min_length=1, max_length=80)
    description: typing.Optional[str] = \
        pydantic.Field(default=None, min_length=1)
    redundancy: typing.Optional[int] = pydantic.Field(default=3, ge=1)
    guideline: typing.Optional[str] = \
        pydantic.Field(default=None)


class Project(ProjectBase):
    id: typing.Optional[int] = pydantic.Field(default=None)
