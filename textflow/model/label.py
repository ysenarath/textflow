""" Label Entity """

from textflow.services.base import database as db


class Label(db.Model):
    """ Label Entity """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, default=1)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete="CASCADE"), nullable=False)
