"""Annotation model.

This module contains the annotation model.

Classes
-------
AnnotationSpan
Annotation
AnnotationSetLog
AnnotationSet
"""
from typing import List

from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped

from textflow.database import db

__all__ = [
    'Annotation',
    'AnnotationSet',
    'AnnotationSetLog',
    'AnnotationSpan',
]


class AnnotationSpan(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer)
    length = db.Column(db.Integer)
    annotation_id = db.Column(db.Integer, db.ForeignKey(
        'annotation.id'), unique=True, nullable=False)

    @hybrid_property
    def end(self) -> int:
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

    def to_dict(self):
        """Convert to dictionary.

        Returns
        -------
        dict
            Dictionary representation of AnnotationSpan.
        """
        return {
            'id': self.id,
            'start': self.start,
            'length': self.length,
            'annotation_id': self.annotation_id,
        }


# Many to Many relationship between Annotation and Label
annotation_label = Table(
    'annotation_label',
    db.Model.metadata,
    Column('label_id', ForeignKey('label.id'), primary_key=True),
    Column('annotation_id', ForeignKey('annotation.id'), primary_key=True),
    Column('created_on', db.DateTime, server_default=db.func.now()),
    Column('updated_on', db.DateTime, server_default=db.func.now(),
           server_onupdate=db.func.now()),
)


class Annotation(db.Model):
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
    to_dict()
        Convert to dictionary.
    """
    id = db.Column(db.Integer, primary_key=True)
    span = db.relationship('AnnotationSpan', backref='annotation',
                           uselist=False, cascade="all, delete-orphan")
    labels: Mapped[List['Label']] = db.relationship(  # noqa # type: ignore
        secondary='annotation_label'
    )
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(),
        server_onupdate=db.func.now()
    )
    annotation_set_id = db.Column(db.Integer, db.ForeignKey(
        'annotation_set.id'), nullable=False)

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

    def to_dict(self):
        """Convert to dictionary.

        Returns
        -------
        dict
            Dictionary representation of Annotation.
        """
        return {
            'id': self.id,
            'span': self.span.to_dict() if self.span else None,
            'labels': [label.to_dict() for label in self.labels],
            'annotation_set_id': self.annotation_set_id,
        }


class AnnotationSetLog(db.Model):
    """AnnotationSetLog Entity - keeps track of changes to an AnnotationSet.

    Attributes
    ----------
    id : int
        Primary key.
    annotation_id : int
        Annotation id.
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
    id = db.Column(db.Integer, primary_key=True)
    annotation_set_id = db.Column(
        db.Integer, db.ForeignKey('annotation_set.id'), nullable=False
    )
    flagged = db.Column(db.Boolean(), nullable=False, default=False)
    skipped = db.Column(db.Boolean(), nullable=False, default=False)
    completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(),
        server_onupdate=db.func.now()
    )


class AnnotationSet(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey(
        'document.id', ondelete="CASCADE"), nullable=False)
    document = db.relationship('Document', backref=db.backref(
        'annotation_set', lazy=True, cascade="all,delete"), uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref(
        'annotation_set', lazy=True), uselist=False
    )
    annotations = db.relationship(
        'Annotation', backref='annotation_set',
        lazy=True, cascade='all, delete'
    )
    completed = db.Column(db.Boolean(), nullable=False, default=False)
    flagged = db.Column(db.Boolean(), nullable=False, default=False)
    skipped = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(),
        server_onupdate=db.func.now()
    )
    logger = db.relationship(
        'AnnotationSetLog', backref='annotation_set',
        lazy=True, cascade='all, delete'
    )

    __table_args__ = (db.UniqueConstraint('user_id', 'document_id'),)

    def to_dict(self):
        """Convert to dictionary.

        Returns
        -------
        dict
            Dictionary representation of AnnotationSet.
        """
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'completed': self.completed,
            'flagged': self.flagged,
            'skipped': self.skipped,
            'annotations': [a.to_dict() for a in self.annotations],
        }


@db.event.listens_for(AnnotationSet, 'after_insert')
@db.event.listens_for(AnnotationSet, 'after_update')
def log_update_event(mapper, connection, target):
    """Log AnnotationSet update event.

    Parameters
    ----------
    mapper : Mapper
        Mapper.
    connection : Connection
        Connection.
    target : AnnotationSet
        AnnotationSet object.

    Returns
    -------
    None
        None.
    """
    log = AnnotationSetLog(annotation_set_id=target.id)
    log.completed = target.completed
    log.flagged = target.flagged
    log.skipped = target.skipped
    db.session.add(log)
