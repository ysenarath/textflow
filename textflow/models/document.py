"""Document model.

This module contains the Document model.

Classes
-------
Document
"""

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property

from textflow.models.base import mapper_registry, ModelMixin

__all__ = [
    'Document',
]


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class Document(ModelMixin):
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
    __table__ = sa.Table(
        'document',
        mapper_registry.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('source_id', sa.String(128), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('meta', sa.JSON, nullable=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id'),
                  nullable=False),

    )

    @hybrid_property
    def id_str(self):
        return self.source_id

    @id_str.setter
    def id_str(self, value):
        self.source_id = value
