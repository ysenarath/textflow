"""Document model.

This module contains the Document model.

Classes
-------
Document
"""
import html

from textflow.database import db

__all__ = [
    'Document',
]


class Document(db.Model):
    """Document Entity. Contains text and meta information.

    Attributes
    ----------
    id : int
        Primary key.
    source_id : str
        Original id from source file.
    text : str
        Text of document.
    meta : dict
        Meta information of document.
    project_id : int
        Project id.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # id_str is different from the id field because it is used to store the
    # original id from the source file
    id_str = db.Column('source_id', db.String(128), nullable=True)
    text = db.Column(db.Text(), nullable=False)
    meta = db.Column(db.JSON, nullable=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project.id'),
        nullable=False
    )

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        # TODO: fix \n repr
        text = self.text.replace('\n', ' ')
        self.text = html.escape(text)

    def __getitem__(self, item):
        return html.unescape(self.text.__getitem__(item))

    @property
    def source_id(self):
        return self.id_str

    @source_id.setter
    def source_id(self, value):
        self.id_str = value

    def to_dict(self):
        return {
            'id_str': self.id_str,
            'id': self.id,
            'text': self.text,
            'meta': self.meta,
            'project_id': self.project_id,
        }
