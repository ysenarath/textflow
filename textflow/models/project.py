"""Project model.

This module contains the Project model.

Classes
-------
Project
"""
import dataclasses
import logging
import typing

import jinja2

import pydantic


from textflow.database import db

__all__ = [
    'Project',
]

logger = logging.getLogger(__name__)


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class Project(db.ModelMixin):
    """This model contains the project information.

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
        Tasks of project (ordedred by Task.order).
    """
    __table__ = db.Table(
        'project',
        db.mapper_registry.metadata,
        db.Column('id', db.Integer, primary_key=True, autoincrement=True),
        db.Column('name', db.String(80), nullable=False),
        db.Column('description', db.Text,
                  default='Description is not available.'),
        db.Column('redundancy', db.Integer, default=3, nullable=True),
        db.Column('guideline_template', db.Text, default=None, nullable=True),
    )

    __mapper_args__ = {
        'properties': dict(
            documents=db.relationship('Document', backref='project'),
            users=db.relationship('Assignment', backref='project',
                                  lazy=True, cascade='all, delete'),
            jobs=db.relationship('BackgroundJob', backref='project',
                                 lazy=True),
            tasks=db.relationship('Task', backref='project', lazy=True,
                                  order_by='Task.order'),
        )
    }

    name: str = pydantic.Field()
    id: typing.Optional[int] = pydantic.Field(default=None)
    description: typing.Optional[str] = \
        pydantic.Field(default=None)
    redundancy: typing.Optional[int] = pydantic.Field(default=3)
    guideline_template: typing.Optional[str] = \
        pydantic.Field(default=None)

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
