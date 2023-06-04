import math
import typing

import pydantic
from pydantic.generics import GenericModel

# from textflow.models import ModelType
ModelType = typing.TypeVar('ModelType')


__all__ = [
    'PaginationArgs',
    'Pagination',
]


@pydantic.dataclasses.dataclass
class PaginationArgs:
    page: int = pydantic.Field(default=1)
    per_page: int = pydantic.Field(default=10, le=100)
    error_out: bool = pydantic.Field(default=False)


class Pagination(GenericModel, typing.Generic[ModelType]):
    # The current page number (1 indexed).
    page: int
    # The number of items to be displayed on a page.
    per_page: int
    # The total number of items matching the query.
    total: int
    # The items for the current page.
    items: typing.List[ModelType]
    # will be initialized by __post_init__
    pages: typing.Optional[int] = pydantic.Field(default=None)
    prev_num: typing.Optional[int] = pydantic.Field(default=None)
    has_prev: typing.Optional[bool] = pydantic.Field(default=None)
    next_num: typing.Optional[int] = pydantic.Field(default=None)
    has_next: typing.Optional[bool] = pydantic.Field(default=None)

    def __init__(self, **kwargs):
        super(Pagination, self).__init__(**kwargs)
        # The items for the current page.
        if self.per_page == 0:
            self.pages = 0
        else:
            #: The total number of pages.
            self.pages = int(math.ceil(self.total / float(self.per_page)))
        #: Number of the previous page.
        self.prev_num = self.page - 1
        #: True if a previous page exists.
        self.has_prev = self.page > 1
        #: Number of the next page.
        self.next_num = self.page + 1
        #: True if a next page exists.
        self.has_next = self.page < self.pages
