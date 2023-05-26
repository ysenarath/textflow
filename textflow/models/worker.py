"""BackgroundJob entity.

This module contains the BackgroundJob entity which is used to keep track of
background jobs that are running

Classes
-------
BackgroundJob
"""
from textflow.database import db

__all__ = [
    'BackgroundJob',
]


class BackgroundJob(db.Model):
    """BackgroundJob Entity.

    This entity is used to keep track of background jobs that are running.

    Attributes
    ----------
    id : str
        Unique id of the task that is running (e.g., from celery).
    user_id : int
        User id of the user who started the task is stored here to keep track 
        of who started the task (todo: and who can cancel it)
    project_id : int
        Project id of the project that the task is related to.
    hash : str
        Hash of a task is the hash of the task's parameters so that we can
        identify if a task with the same parameters has already been run
        (or is running) and avoid running it again simultaneously.
    """
    # task id is a unique id of the task that is running (e.g., from celery)
    id = db.Column(db.String(128), primary_key=True)
    # user id of the user who started the task is stored here to keep track of
    # who started the task (todo: and who can cancel it)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # project id of the project that the task is related to
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False
    )
    # hash of a task is the hash of the task's parameters so that we can
    # identify if a task with the same parameters has already been run
    # (or is running) and avoid running it again simultaneously
    # for example you dont want to delete the documents of a project twice at
    # the same time by same or two users
    hash = db.Column(db.String(512), nullable=False, default='default')

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'hash': self.hash,
        }
