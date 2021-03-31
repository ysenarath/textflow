""" Project Entity """

import logging

import jinja2

from textflow.model.dataset import datasets
from textflow.model.model import models
from textflow.services.base import database as db

logger = logging.getLogger(__name__)


class Project(db.Model):
    """ Project object contains project information """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default='No description provided.')
    type = db.Column(db.String(80), nullable=False)
    documents = db.relationship('Document', backref='project')
    labels = db.relationship('Label', backref='project', lazy=True, cascade='all, delete')
    users = db.relationship('Assignment', backref='project', lazy=True, cascade='all, delete')
    redundancy = db.Column(db.Integer, default=3)
    guideline_template = db.Column(db.String, nullable=True)

    def render_guideline(self):
        """ Meta renderer used to create header for document when annotating.

        :return: rendered header template
        """
        if self.guideline_template is None:
            return None
        return jinja2.Template(self.guideline_template).render(project=self)

    def register(self, type, name='default'):
        """Register plugin for this project.

        :param type: type of plugin
        :param name: name of plugin
        :return: registered object
        """
        if type == 'dataset':
            return datasets.register(self.id, name=name)
        elif type == 'model':
            return models.register(self.id, name=name)
        else:
            return None
