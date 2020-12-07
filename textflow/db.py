""" Contains db object. """

from flask_sqlalchemy import BaseQuery, SQLAlchemy


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


db = SQLAlchemy(query_class=ExtendedQuery)
