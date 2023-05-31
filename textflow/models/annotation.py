"""Annotation model.

This module contains the annotation model.

Classes
-------
AnnotationSpan
Annotation
AnnotationSet
"""
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from textflow.models.base import mapper_registry, ModelMixin

__all__ = [
    'Annotation',
    'AnnotationSet',
    'AnnotationSpan',
]


@mapper_registry.mapped
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


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class AnnotationLabel(ModelMixin):
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
    __table__ = sa.Table(
        'annotation_label',
        mapper_registry.metadata,
        sa.Column(
            'label_id', sa.Integer, sa.ForeignKey('label.id'),
            primary_key=True
        ),
        sa.Column(
            'annotation_id', sa.Integer, sa.ForeignKey('annotation.id'),
            primary_key=True
        ),
        sa.Column('created_on', sa.DateTime, server_default=sa.func.now()),
        sa.Column(
            'updated_on', sa.DateTime,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now()
        ),
    )


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class Annotation(ModelMixin):
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
    __table__ = sa.Table(
        'annotation',
        mapper_registry.metadata,
        sa.Column(
            'id', sa.Integer, primary_key=True,
            autoincrement=True
        ),
        sa.Column(
            'annotation_set_id', sa.Integer,
            sa.ForeignKey('annotation_set.id'), nullable=False
        ),
        sa.Column(
            'created_on', sa.DateTime, server_default=sa.func.now()
        ),
        sa.Column(
            'updated_on', sa.DateTime, server_default=sa.func.now(),
            server_onupdate=sa.func.now()
        ),
    )
    __mapper_args__ = {  # type: ignore
        "properties": dict(
            span=sa.orm.relationship(
                'AnnotationSpan', backref='annotation',
                uselist=False, cascade="all, delete-orphan"
            ),
            labels=sa.orm.relationship(
                'Label', secondary='annotation_label'
            )
        )
    }

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


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class AnnotationSet(ModelMixin):
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
    __table__ = sa.Table(
        'annotation_set',
        mapper_registry.metadata,
        sa.Column(
            'id', sa.Integer, primary_key=True,
            autoincrement=True
        ),
        sa.Column(
            'document_id', sa.Integer,
            sa.ForeignKey('document.id', ondelete="CASCADE"),
            nullable=False
        ),
        sa.Column(
            'user_id', sa.Integer,
            sa.ForeignKey('user.id', ondelete="CASCADE"),
            nullable=False
        ),
        sa.Column(
            'completed', sa.Boolean(), nullable=False, default=False
        ),
        sa.Column(
            'flagged', sa.Boolean(), nullable=False, default=False
        ),
        sa.Column(
            'skipped', sa.Boolean(), nullable=False, default=False
        ),
        sa.Column(
            'created_on', sa.DateTime, server_default=sa.func.now()
        ),
        sa.Column(
            'updated_on', sa.DateTime, server_default=sa.func.now(),
            server_onupdate=sa.func.now()
        ),
    )

    __mapper_args__ = {  # type: ignore
        "properties": dict(
            document=sa.orm.relationship(
                'Document',
                backref=sa.orm.backref(
                    'annotation_set', lazy=True, cascade="all,delete"),
                uselist=False
            ),
            user=sa.orm.relationship(
                'User', backref=sa.orm.backref('annotation_set', lazy=True),
                uselist=False
            ),
            annotations=sa.orm.relationship(
                'Annotation', backref='annotation_set',
                lazy=True, cascade='all, delete'
            )
        )
    }

    __table_args__ = (
        sa.UniqueConstraint('user_id', 'document_id'),
    )
