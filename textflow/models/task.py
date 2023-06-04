"""Task model.

This module contains the Task model.

Classes
-------
Task
"""
import logging
import json

from textflow.database import db

logger = logging.getLogger(__name__)

__all__ = [
    'Task',
]


class Task(db.Model):
    """Task Entity. Contains labels and condition.

    Attributes
    ----------
    id : int
        Primary key.
    title : str
        Title of task.
    description : str
        Description of task.
    type : str
        Type of task.
    project_id : int
        Project id of task.
    labels : list of Label
        Labels of task.
    condition : dict
        Condition of task.
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(80), default=None)
    description = db.Column(db.Text, default=None)
    type = db.Column(db.String(80), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)
    order = db.Column(db.Integer, default=1)
    labels = db.relationship('Label', backref='task', lazy=True,
                             cascade='all, delete', order_by='Label.order')
    condition = db.Column(db.JSON)

    def to_dict(self):
        """Convert task to dict.

        Returns
        -------
        dict
            Task as dict.
        """
        condition = None
        if self.condition is not None:
            condition = json.loads(self.condition)
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'type': self.type,
            'labels': [label.to_dict() for label in self.labels],
            'condition': condition,
        }
