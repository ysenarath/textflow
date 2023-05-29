"""Annotation model.

This module contains the annotation model.

Classes
-------
AnnotationSpan
Annotation
AnnotationSet
"""
import datetime
import typing

import pydantic

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from textflow.database.base import ModelMixin

__all__ = [
    'Annotation',
    'AnnotationSet',
    'AnnotationSpan',
]


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class AnnotationSpan(ModelMixin):
    """Annotation-Span Entity - contains start and length.

    Attributes
    ----------
    id : int
        Primary key.
    start : int
        Start of span.
    length : int
        Length of span.
    annotation_id : int
        Annotation id.
    """
    __table__ = sa.Table(
        'annotation_span',
        mapper_registry.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('start', sa.Integer, nullable=False),
        sa.Column('length', sa.Integer, nullable=False),
        sa.Column(
            'annotation_id', sa.Integer, sa.ForeignKey('annotation.id'),
            unique=True, nullable=False
        ),
    )

    start: int = pydantic.Field()
    length: int = pydantic.Field()
    annotation_id: int = pydantic.Field()
    id: typing.Optional[int] = pydantic.Field(default=None)

    @hybrid_property
    def end(self):
        """Get end of span.

        Returns
        -------
        int
            End of span.
        """
        return self.start + self.length

    def get_slice(self):
        """Get slice from span.

        Returns
        -------
        slice
            Slice object.
        """
        return slice(self.start, self.start + self.length)


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class AnnotationLabel(db.ModelMixin):
    """AnnotationLabel Entity - contains label_id and annotation_id.

    Attributes
    ----------
    label_id : int
        Label id.
    annotation_id : int
        Annotation id.
    created_on : datetime
        Created on.
    updated_on : datetime
        Updated on.
    """
    __table__ = db.Table(
        'annotation_label',
        db.mapper_registry.metadata,
        db.Column(
            'label_id', db.Integer, db.ForeignKey('label.id'),
            primary_key=True
        ),
        db.Column(
            'annotation_id', db.Integer, db.ForeignKey('annotation.id'),
            primary_key=True
        ),
        db.Column('created_on', db.DateTime, server_default=db.func.now()),
        db.Column(
            'updated_on', db.DateTime,
            server_default=db.func.now(),
            server_onupdate=db.func.now()
        ),
    )

    label_id: int = pydantic.Field()
    annotation_id: int = pydantic.Field()
    created_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)
    updated_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class Annotation(db.ModelMixin):
    """Annotation Entity - contains annotations by a user for a document.

    Attributes
    ----------
    id : int
        Primary key.
    span : AnnotationSpan
        AnnotationSpan object.
    labels : List[Label]
        List of Label objects.
    created_on : datetime
        Created on.
    updated_on : datetime
        Updated on.
    annotation_set_id : int
        AnnotationSet id.

    Methods
    -------
    get_slice()
        Get slice from span.
    """
    __table__ = db.Table(
        'annotation',
        db.mapper_registry.metadata,
        db.Column(
            'id', db.Integer, primary_key=True,
            autoincrement=True
        ),
        db.Column(
            'annotation_set_id', db.Integer,
            db.ForeignKey('annotation_set.id'), nullable=False
        ),
        db.Column(
            'created_on', db.DateTime, server_default=db.func.now()
        ),
        db.Column(
            'updated_on', db.DateTime, server_default=db.func.now(),
            server_onupdate=db.func.now()
        ),
    )
    __mapper_args__ = {  # type: ignore
        "properties": dict(
            span=db.relationship(
                'AnnotationSpan', backref='annotation',
                uselist=False, cascade="all, delete-orphan"
            ),
            labels=db.relationship(
                'Label', secondary='annotation_label'
            )
        )
    }

    annotation_set_id: int = pydantic.Field()
    id: typing.Optional[int] = pydantic.Field(default=None)
    created_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(
        default=None)
    updated_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(
        default=None)

    def get_slice(self):
        """Get slice from span.

        Returns
        -------
        slice
            Slice object.
        """
        if self.span is None:
            return slice(None, None, None)
        return self.span.slice()


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class AnnotationSet(db.ModelMixin):
    """AnnotationSet Entity - contains annotations by a user for a document.

    Attributes
    ----------
    id : int
        Primary key.
    document_id : int
        Document id.
    document : Document
        Document object.
    user_id : int
        User id.
    user : User
        User object.
    annotations : List[Annotation]
        List of Annotation objects.
    completed : bool
        Completed.
    flagged : bool
        Flagged.
    skipped : bool
        Skipped.
    created_on : datetime
        Created on.
    updated_on : datetime
        Updated on.
    """
    __table__ = db.Table(
        'annotation_set',
        db.mapper_registry.metadata,
        db.Column(
            'id', db.Integer, primary_key=True,
            autoincrement=True
        ),
        db.Column(
            'document_id', db.Integer,
            db.ForeignKey('document.id', ondelete="CASCADE"),
            nullable=False
        ),
        db.Column(
            'user_id', db.Integer,
            db.ForeignKey('user.id', ondelete="CASCADE"),
            nullable=False
        ),
        db.Column(
            'completed', db.Boolean(), nullable=False, default=False
        ),
        db.Column(
            'flagged', db.Boolean(), nullable=False, default=False
        ),
        db.Column(
            'skipped', db.Boolean(), nullable=False, default=False
        ),
        db.Column(
            'created_on', db.DateTime, server_default=db.func.now()
        ),
        db.Column(
            'updated_on', db.DateTime, server_default=db.func.now(),
            server_onupdate=db.func.now()
        ),
    )

    __mapper_args__ = {  # type: ignore
        "properties": dict(
            document=db.relationship(
                'Document',
                backref=db.backref(
                    'annotation_set', lazy=True, cascade="all,delete"),
                uselist=False
            ),
            user=db.relationship(
                'User', backref=db.backref('annotation_set', lazy=True),
                uselist=False
            ),
            annotations=db.relationship(
                'Annotation', backref='annotation_set',
                lazy=True, cascade='all, delete'
            )
        )
    }

    __table_args__ = (
        db.UniqueConstraint('user_id', 'document_id'),
    )

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
