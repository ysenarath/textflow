"""Project schema.

Classes
-------
Project
"""
import logging
import typing

import jinja2
import pydantic

from textflow.schemas.base import Schema


__all__ = [
    'Project',
    'UpdateProject',
]

logger = logging.getLogger(__name__)


class ProjectBase(Schema):
    name: str = pydantic.Field()
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


class Project(ProjectBase):
    id: typing.Optional[int] = pydantic.Field(default=None)
