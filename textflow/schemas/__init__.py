"""This module contains all the schemas used by the application.

Classes
-------
Annotation
AnnotationSet
AnnotationSpan
Document
DocumentBase
Label
Project
Assignment
User
BackgroundJob
Task
TaskSchema
"""
from textflow.schemas.annotation import (
    AnnotationSet,
    Annotation,
    AnnotationSpan,
)
from textflow.schemas.base import Schema
from textflow.schemas.document import Document, DocumentBase
from textflow.schemas.label import Label
from textflow.schemas.project import Project, ProjectBase
from textflow.schemas.task import Task
from textflow.schemas.user import (
    Assignment,
    User,
    RoleEnum,
    ThemeEnum,
)
from textflow.schemas.worker import BackgroundJob


__all__ = [
    'Annotation',
    'AnnotationSet',
    'AnnotationSpan',
    'Document',
    'DocumentBase',
    'Project',
    'ProjectBase',
    'Label',
    'Assignment',
    'User',
    'BackgroundJob',
    'Task',
    'Schema',
    'RoleEnum',
    'ThemeEnum',
]
