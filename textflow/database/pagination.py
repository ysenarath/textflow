import math

from flask import request as flask_request, Request


__all__ = [
    'PaginationArgs'
]


class PaginationArgs(object):
    def __init__(self, request=None):
        """Returns pagination parameters from request.

        Parameters
        ----------
        request : flask.Request or dict
            Request object or params.

        Returns
        -------
        dict
            Pagination parameters.
        """
        if request is None:
            request = flask_request
        if isinstance(request, Request):
            request_args = request.args
        else:
            request_args = request
        try:
            page = int(request_args['page'])
        except (KeyError, ValueError):
            page = 1
        if page < 1:
            page = 1
        self.page = page
        try:
            per_page = int(request_args['per_page'])
        except (KeyError, ValueError):
            per_page = 10
        if per_page < 1:
            per_page = 1
        self.per_page = per_page
        self.error_out = False

    def to_dict(self):
        """Returns pagination parameters as dictionary.

        Returns
        -------
        dict
            Pagination parameters.
        """
        return {
            'page': self.page,
            'per_page': self.per_page,
            'error_out': self.error_out,
        }


class Pagination(object):
    """Class returned by `Query.paginate`. You can also construct
    it from any other SQLAlchemy query object if you are working
    with other libraries. Additionally it is possible to pass
    ``None`` as query object in which case the `prev` and `next`
    will no longer work.
    """

    def __init__(self, query, page, per_page, total, items):
        #: The query object that was used to create this pagination object.
        self.query = query
        #: The current page number (1 indexed).
        self.page = page
        #: The number of items to be displayed on a page.
        self.per_page = per_page
        #: The total number of items matching the query.
        self.total = total
        #: The items for the current page.
        self.items = items
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

    def prev(self, error_out=False):
        """Returns a `Pagination` object for the previous page."""
        assert self.query is not None, \
            'a query object is required for this method to work'
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    def next(self, error_out=False):
        """Returns a `Pagination` object for the next page."""
        assert self.query is not None, \
            'a query object is required for this method to work'
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    def iter_pages(
        self,
        *,
        left_edge: int = 2,
        left_current: int = 2,
        right_current: int = 4,
        right_edge: int = 2,
    ):
        """"""
        pages_end = self.pages + 1

        if pages_end == 1:
            return

        left_end = min(1 + left_edge, pages_end)
        yield from range(1, left_end)

        if left_end == pages_end:
            return

        mid_start = max(left_end, self.page - left_current)
        mid_end = min(self.page + right_current + 1, pages_end)

        if mid_start - left_end > 0:
            yield None

        yield from range(mid_start, mid_end)

        if mid_end == pages_end:
            return

        right_start = max(mid_end, pages_end - right_edge)

        if right_start - mid_end > 0:
            yield None

        yield from range(right_start, pages_end)
