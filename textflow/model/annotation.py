""" Annotation Entity """

from simtex.db import db
from sqlalchemy.exc import SQLAlchemyError


class AnnotationSpan(db.Model):
    """ Annotation-Span Entity - contains start and length """
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer)
    length = db.Column(db.Integer)
    annotation_id = db.Column(db.Integer, db.ForeignKey('annotation.id'), nullable=False)


class Annotation(db.Model):
    """ Annotation Entity - contains annotation with span or whole document """
    id = db.Column(db.Integer, primary_key=True)
    span = db.relationship('AnnotationSpan', backref='annotation', uselist=False,
                           cascade="all, delete-orphan")
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'), nullable=False)
    label = db.relationship('Label', backref=db.backref('annotations', lazy=True), uselist=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    annotation_set_id = db.Column(db.Integer, db.ForeignKey('annotation_set.id'), nullable=False)


class AnnotationSet(db.Model):
    """ AnnotationSet Entity - contains annotations by a user for a document. """
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    document = db.relationship('Document', backref=db.backref('annotation_set', lazy=True), uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('annotation_set', lazy=True), uselist=False)
    annotations = db.relationship('Annotation', backref='annotation_set', lazy=True)
    complete = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def get_annotation(self, value):
        """ gets annotations with the value from the annotations

        :param value: value of label to search
        :return: annotation with provided value if exists other wise none
        """
        for a in self.annotations:
            if a.label.value == value:
                return a
        return None

    @staticmethod
    def get_or_create(current_user, doc_id):
        """ Returns annotation set

        :param current_user: user
        :param doc_id: document id
        :return: annotation set for user document pair
        """
        annotation_set = AnnotationSet.query \
            .filter(AnnotationSet.document_id == doc_id, AnnotationSet.user_id == current_user.id) \
            .first()
        if annotation_set is None:
            annotation_set = AnnotationSet(document_id=doc_id, user_id=current_user.id)
            db.session.add(annotation_set)
            db.session.commit()
        return annotation_set

    def add_annotation(self, annotation):
        """ Add annotation to set of annotations

        :param annotation:
        :return:
        """
        try:
            self.annotations.append(annotation)
            db.session.commit()
            return True
        except SQLAlchemyError as err:
            db.session.rollback()
            return False
