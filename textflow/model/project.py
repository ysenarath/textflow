""" Project Entity """

import logging

import jinja2

from textflow.db import db

logger = logging.getLogger(__name__)


class Project(db.Model):
    """ Project object contains project information """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default='Description ')
    type = db.Column(db.String(80), nullable=False)
    documents = db.relationship('Document', backref='project')
    labels = db.relationship('Label', backref='project', lazy=True)
    users = db.relationship('Assignment', backref='project', lazy=True)
    redundancy = db.Column(db.Integer, default=3)
    header_template = db.Column(db.String, nullable=True)

    def render_header(self, document):
        """ Meta renderer used to create header for document when annotating.

        :param document: document to pass when rendering header.
        :return: rendered header template
        """
        if self.header_template is None:
            return None
        return jinja2.Template(self.header_template).render(document=document)
