"""Project model.

This module contains the Project model.

Classes
-------
Project
"""
import logging

import jinja2

from textflow.database import db

logger = logging.getLogger(__name__)

__all__ = [
    'Project',
]


class Project(db.Model):
    """Project Entity. Contains documents and users.

    Attributes
    ----------
    id : int
        Primary key.
    name : str
        Name of project.
    description : str
        Description of project.
    documents : list of Document
        Documents of project.
    users : list of Assignment
        Users of project.
    redundancy : int
        Redundancy of number of annotations per document user.
    guideline_template : str
        Template for guideline.
    jobs : list of BackgroundJob
        Background jobs related to this project.
    tasks : list of Task
        Tasks of project.
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default='No description provided.')
    documents = db.relationship('Document', backref='project')
    users = db.relationship('Assignment', backref='project',
                            lazy=True, cascade='all, delete')
    redundancy = db.Column(db.Integer, default=3)
    guideline_template = db.Column(db.String, nullable=True)
    jobs = db.relationship('BackgroundJob', backref='project', lazy=True)
    tasks = db.relationship('Task', backref='project', lazy=True)

    def render_guideline(self):
        """Render the guideline template.

        Returns
        -------
        str
            Rendered guideline template.
        """
        if self.guideline_template is None:
            return None
        return jinja2.Template(self.guideline_template).render(project=self)

    def to_dict(self):
        """Convert project to dict.

        Returns
        -------
        dict
            Project as dict.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'redundancy': self.redundancy,
            'guideline_template': self.guideline_template,
            'tasks': [task.to_dict() for task in self.tasks],
        }
