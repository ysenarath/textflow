"""This module contains all the models used by the application.

The modules in this package are independent of the database package.
    The models described are mapped to the database using the SQLAlchemy ORM.
    The mapper is located at `textflow.models.mapper_registry`. And exposed by 
    this module('s __init__.py).

Classes
-------
Annotation
AnnotationSet
AnnotationSpan
Document
Label
Project
User
RefreshToken
Assignment
Task
TaskSchema
"""
from textflow.models.annotation import (
    AnnotationSet,
    Annotation,
    AnnotationSpan,
)
from textflow.models.base import mapper_registry, ModelType
from textflow.models.document import Document
from textflow.models.label import Label
from textflow.models.project import Project
from textflow.models.task import Task
from textflow.models.user import (
    User,
    Assignment,
    RefreshToken,
)


__all__ = [
    'Annotation',
    'AnnotationSet',
    'AnnotationSpan',
    'Document',
    'Project',
    'Label',
    'User',
    'Assignment',
    'RefreshToken',
    'Task',
    'mapper_registry',
    'ModelType',
]
