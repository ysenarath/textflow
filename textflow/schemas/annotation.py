"""Annotation schema.

Classes
-------
Annotation
AnnotationSet
AnnotationSpan
AnnotationLabel
"""
import datetime
import typing

import pydantic

from textflow.schemas.base import Schema

__all__ = [
    'Annotation',
    'AnnotationSet',
    'AnnotationSpan',
    'AnnotationLabel',
]


class AnnotationSpan(Schema):
    start: int = pydantic.Field()
    length: int = pydantic.Field()
    annotation_id: int = pydantic.Field()
    id: typing.Optional[int] = pydantic.Field(default=None)


class AnnotationLabel(Schema):
    label_id: int = pydantic.Field()
    annotation_id: int = pydantic.Field()
    created_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)
    updated_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)


class Annotation(Schema):
    annotation_set_id: int = pydantic.Field()
    id: typing.Optional[int] = pydantic.Field(default=None)
    created_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)
    updated_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)


class AnnotationSet(Schema):
    document_id: int = pydantic.Field()
    user_id: int = pydantic.Field()
    completed: bool = pydantic.Field(default=False)
    flagged: bool = pydantic.Field(default=False)
    skipped: bool = pydantic.Field(default=False)
    id: typing.Optional[int] = pydantic.Field(default=None)
    created_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)
    updated_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)
