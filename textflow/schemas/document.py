"""Document schema.

Classes
-------
Document
"""
import html
import typing

import pydantic

from textflow.schemas.base import Schema


__all__ = [
    'Document',
]


class DocumentBase(Schema):
    text: str = pydantic.Field()
    # id_str is different from the id field because it is used to store the
    # original id from the source file
    source_id: typing.Optional[str] = pydantic.Field(default=None)
    meta: typing.Optional[pydantic.Json] = \
        pydantic.Field(default=None)

    def __post_init_post_parse__(self):
        text = self.text.replace('\n', ' ')
        self.text = html.escape(text)

    def __getitem__(self, item):
        return html.unescape(self.text.__getitem__(item))


class Document(DocumentBase):
    id: typing.Optional[int] = pydantic.Field(default=None)
    project_id: int = pydantic.Field()
