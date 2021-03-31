""" Contains db object """
from types import SimpleNamespace

from flask_sqlalchemy import BaseQuery, SQLAlchemy

__all__ = [
    'database',
    'service',
]


class ExtendedQuery(BaseQuery):
    """ Extend query to support additional functions. """

    def get_or(self, ident, default=None):
        """ gets object if exist else return default

        :param ident: object identifier
        :param default: default to return if obj does not exist
        :return: result or default
        """
        result = self.get(ident)
        return default if result is None else result


class Service:
    """ Query class """

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        ctx = SimpleNamespace(ignore_user=False)
        return self.fn(ctx, *args, **kwargs)

    def ignore_user(self, *args, **kwargs):
        """Try to run command as admin.

        This will disable all user level constrains.

        :param args: args for fn
        :param kwargs: kwargs for fn
        """
        ctx = SimpleNamespace(ignore_user=True)
        return self.fn(ctx, *args, **kwargs)


def service(fn):
    """Creates and returns query callable.

    :param fn: Function to decorate.
    :return: Query
    """
    return Service(fn)


database = SQLAlchemy(query_class=ExtendedQuery)
