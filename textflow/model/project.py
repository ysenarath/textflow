""" Project Entity """

import logging

import jinja2
from simtex.db import db
from simtex.model.annotation import AnnotationSet
from simtex.model.document import Document
from simtex.model.user import User
from sqlalchemy import or_

logger = logging.getLogger(__name__)


class Project(db.Model):
    """ Project object contains project information """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default='Description ')
    type = db.Column(db.String(80), nullable=False)
    documents = db.relationship('Document', backref='project')
    labels = db.relationship('Label', backref='project', lazy=True)
    users = db.relationship('User', backref='project', lazy=True)
    redundancy = db.Column(db.Integer, default=3)
    header_template = db.Column(db.String, nullable=True)

    def next_document(self, user: User):
        """ Returns next document for annotation by provided user.

        :param user: user
        :return: document if exist else none
        """
        # get documents that were only annotated by less than
        #  -  required redundancy (project.redundancy) amount
        query = Document.query \
            .filter_by(project_id=self.id) \
            .outerjoin(AnnotationSet, AnnotationSet.document_id == Document.id) \
            .filter(or_(AnnotationSet.completed.is_(False),
                        AnnotationSet.user_id != user.id,
                        AnnotationSet.completed.is_(None)))
        for document in query.all():
            annotation_users = set(a.user.username for a in document.annotation_set if a.completed)
            if len(annotation_users) < self.redundancy and \
                    (user is None or user.username not in annotation_users):
                return document
        return None

    def render_header(self, document):
        """ Meta renderer used to create header for document when annotating.

        :param document: document to pass when rendering header.
        :return: rendered header template
        """
        return jinja2.Template(self.header_template).render(document=document)
