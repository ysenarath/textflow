from textflow.services.base import database as db

__all__ = [
    'Task',
]


class Task(db.Model):
    """ Project User Role Assignment Entity """
    # task id is a unique id of the celery task that is running
    id = db.Column(db.String(128), primary_key=True)
    # hash of a task is the hash of the task's parameters so that we can
    # identify if a task with the same parameters has already been run (or is running)
    # and avoid running it again simultaneously
    # for example you dont want to delete the documents of a project twice at the same time by same or two users
    hash = db.Column(db.String(512), nullable=False, default='default')
    # user id of the user who started the task is stored here to keep track of who started 
    # the task (todo: and who can cancel it)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # project id of the project that the task is related to
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
