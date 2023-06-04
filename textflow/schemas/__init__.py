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
RefreshToken
TaskBase
Task
TaskSchema

Enums
-----
UserRoleEnum
AssignmentRoleEnum
ThemeEnum
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
from textflow.schemas.task import Task, TaskBase
from textflow.schemas.user import (
    User,
    RefreshToken,
    Assignment,
    UserRoleEnum,
    AssignmentRoleEnum,
    ThemeEnum,
)


__all__ = [
    'Annotation',
    'AnnotationSet',
    'AnnotationSpan',
    'Document',
    'DocumentBase',
    'Project',
    'ProjectBase',
    'Label',
    'User',
    'Assignment',
    'Task',
    'TaskBase',
    'RefreshToken',
    'Schema',
    'UserRoleEnum',
    'AssignmentRoleEnum',
    'ThemeEnum',
]
