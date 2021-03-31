""" Document Entity """

import html

from textflow.services.base import database as db


class Document(db.Model):
    """ Document Entity """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_str = db.Column(db.String(128), nullable=True)
    text = db.Column(db.Text(), nullable=False)
    meta = db.Column(db.JSON, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        # TODO: fix \n repr
        text = self.text.replace('\n', ' ')
        self.text = html.escape(text)

    def __getitem__(self, item):
        return html.unescape(self.text.__getitem__(item))
