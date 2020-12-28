""" Annotation Entity """

from textflow.service.base import database as db


class AnnotationSpan(db.Model):
    """ Annotation-Span Entity - contains start and length """
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer)
    length = db.Column(db.Integer)
    annotation_id = db.Column(db.Integer, db.ForeignKey('annotation.id'), unique=True, nullable=False)

    def get_slice(self):
        """ Get slice from span

        :return: slice object
        """
        return slice(self.start, self.start + self.length)


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

    def get_slice(self):
        """  Get slice from span

        :return: slice object
        """
        if self.span is None:
            return slice(None, None, None)
        return self.span.slice()


class AnnotationSet(db.Model):
    """ AnnotationSet Entity - contains annotations by a user for a document. """
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    document = db.relationship('Document', backref=db.backref('annotation_set', lazy=True), uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('annotation_set', lazy=True), uselist=False)
    annotations = db.relationship('Annotation', backref='annotation_set', lazy=True)
    completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    __table_args__ = (db.UniqueConstraint('user_id', 'document_id'),)

    def get_annotation(self, value):
        """ gets annotations with the value from the annotations

        :param value: value of label to search
        :return: annotation with provided value if exists other wise none
        """
        for a in self.annotations:
            if a.label.value == value:
                return a
        return None
