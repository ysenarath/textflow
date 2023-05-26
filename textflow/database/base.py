""" Contains db object """
import math

import sqlalchemy as sa
from flask_sqlalchemy import BaseQuery, SQLAlchemy
from flask_sqlalchemy.model import Model

import json


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


class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        return str(obj)


def sanitize_dict(d):
    """ Remove all non-serializable objects from dict

    :param d: dict
    :return: sanitized dict
    """
    if d is None:
        return None
    if isinstance(d, str):
        return d
    if isinstance(d, (int, float, str, bool)):
        if math.isnan(d):
            return None
        return d
    if isinstance(d, (list, tuple)):
        return [sanitize_dict(v) for v in d]
    if isinstance(d, dict):
        return {key: sanitize_dict(value) for key, value in d.items()}
    return str(d)


class ExtendedModel(Model):
    def to_json(self):
        """ Convert model to json compatible dict.

        :return: json string
        """
        encoded = json.loads(json.dumps(self.to_dict(), cls=ExtendedEncoder))
        return sanitize_dict(encoded)


database = SQLAlchemy(query_class=ExtendedQuery, model_class=ExtendedModel)
