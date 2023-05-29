"""Document model.

This module contains the Document model.

Classes
-------
Document
"""
import dataclasses
import html
import typing

import pydantic

from sqlalchemy.ext.hybrid import hybrid_property

from textflow.database import db

__all__ = [
    'Document',
]


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class Document(db.ModelMixin):
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
    __table__ = db.Table(
        'document',
        db.mapper_registry.metadata,
        db.Column('id', db.Integer, primary_key=True, autoincrement=True),
        db.Column('source_id', db.String(128), nullable=True),
        db.Column('text', db.Text(), nullable=False),
        db.Column('meta', db.JSON, nullable=True),
        db.Column('project_id', db.Integer, db.ForeignKey('project.id'),
                  nullable=False),

    )
    project_id: int = pydantic.Field()
    text: str = pydantic.Field()
    # id_str is different from the id field because it is used to store the
    # original id from the source file
    source_id: typing.Optional[str] = pydantic.Field(default=None)
    meta: typing.Optional[pydantic.Json] = \
        pydantic.Field(default=None)
    id: typing.Optional[int] = pydantic.Field(default=None)

    def __post_init_post_parse__(self):
        text = self.text.replace('\n', ' ')
        self.text = html.escape(text)

    def __getitem__(self, item):
        return html.unescape(self.text.__getitem__(item))

    @hybrid_property
    def id_str(self):
        return self.source_id

    @id_str.setter
    def id_str(self, value):
        self.source_id = value
