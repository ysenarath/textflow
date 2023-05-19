""" Annotation Entity """
from typing import List

from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped


from textflow.services.base import database as db


class AnnotationSpan(db.Model):
    """ Annotation-Span Entity - contains start and length """
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer)
    length = db.Column(db.Integer)
    annotation_id = db.Column(db.Integer, db.ForeignKey(
        'annotation.id'), unique=True, nullable=False)

    @hybrid_property
    def end(self) -> int:
        return self.start + self.length

    def get_slice(self):
        """ Get slice from span

        :return: slice object
        """
        return slice(self.start, self.start + self.length)


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
    """ Annotation Entity - contains annotation with span or whole document """
    id = db.Column(db.Integer, primary_key=True)
    span = db.relationship('AnnotationSpan', backref='annotation',
                           uselist=False, cascade="all, delete-orphan")
    labels: Mapped[List['Label']] = db.relationship(
        secondary='annotation_label')
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    annotation_set_id = db.Column(db.Integer, db.ForeignKey(
        'annotation_set.id'), nullable=False)

    def get_slice(self):
        """  Get slice from span

        :return: slice object
        """
        if self.span is None:
            return slice(None, None, None)
        return self.span.slice()


class AnnotationSetLog(db.Model):
    """ Annotation-Span Entity - contains start and length """
    id = db.Column(db.Integer, primary_key=True)
    annotation_id = db.Column(db.Integer, db.ForeignKey(
        'annotation_set.id'), nullable=False)
    flagged = db.Column(db.Boolean(), nullable=False, default=False)
    skipped = db.Column(db.Boolean(), nullable=False, default=False)
    completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class AnnotationSet(db.Model):
    """ AnnotationSet Entity - contains annotations by a user for a document. """
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey(
        'document.id', ondelete="CASCADE"), nullable=False)
    document = db.relationship('Document', backref=db.backref('annotation_set', lazy=True, cascade="all,delete"),
                               uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref(
        'annotation_set', lazy=True), uselist=False)
    annotations = db.relationship(
        'Annotation', backref='annotation_set', lazy=True, cascade='all, delete')
    completed = db.Column(db.Boolean(), nullable=False, default=False)
    flagged = db.Column(db.Boolean(), nullable=False, default=False)
    skipped = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    logger = db.relationship(
        'AnnotationSetLog', backref='annotation_set', lazy=True, cascade='all, delete')

    __table_args__ = (db.UniqueConstraint('user_id', 'document_id'),)


@db.event.listens_for(AnnotationSet, 'after_insert')
@db.event.listens_for(AnnotationSet, 'after_update')
def log_update_event(mapper, connection, target):
    log = AnnotationSetLog(annotation_id=target.id)
    log.document_id = target.document_id
    log.user_id = target.user_id
    log.completed = target.completed
    log.flagged = target.flagged
    log.skipped = target.skipped
    db.session.add(log)
