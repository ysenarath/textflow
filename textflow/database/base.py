""" Contains db object """
import math
import re
import json

import pydantic
from pydantic import BaseModel

import sqlalchemy as sa
from sqlalchemy import create_engine, Column
from sqlalchemy.orm import (
    backref,
    declared_attr,
    DeclarativeBase,
    Query,
    relationship,
    scoped_session,
    sessionmaker,
    MappedAsDataclass,
)
from sqlalchemy.orm import registry
from sqlalchemy.ext.hybrid import hybrid_property

from textflow.database.pagination import Pagination


__all__ = [
    'database',
]


class BaseQuery(Query):
    """Extend query to support additional functions."""

    DEFAULT_PER_PAGE = 20

    def get_or(self, ident, default=None):
        result = self.get(ident)
        return default if result is None else result

    def paginate(self, page, per_page=20, error_out=True):
        """Return `Pagination` instance using already defined query
        parameters.
        """
        if error_out and page < 1:
            raise IndexError
        if per_page is None:
            per_page = self.DEFAULT_PER_PAGE
        # query.limit(self.per_page).offset(self._query_offset).all()
        query_offset = (page - 1) * per_page
        items = self.limit(per_page).offset(query_offset).all()
        if not items and page != 1 and error_out:
            raise IndexError
        # No need to count if we're on the first page and there are fewer items
        # than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()
        return Pagination(self, page, per_page, total, items)


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


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class ModelMixin(object):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # ThisTable -> this_table
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    # make class functional property called query taking cls as argument
    @classproperty
    def query(cls):
        return database.Session.query(cls)

    def to_json(self):
        encoded = json.loads(json.dumps(self.to_dict(), cls=ExtendedEncoder))
        return sanitize_dict(encoded)

    class Config:
        validate_assignment = True


mapper_registry = registry()


class SQLAlchemy(object):
    def __init__(self, query_class) -> None:
        self.query_class = query_class
        self.Session = None

    def init_config(self, config):
        """Initialize database connection.

        Parameters
        ----------
        uri : str
            Database URI.
        """
        self.engine = create_engine(config["SQLALCHEMY_DATABASE_URI"])
        self.Session = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            query_cls=self.query_class,
        ))

    def init_app(self, app):
        """Initialize database from flask app.

        Parameters
        ----------
        app : Flask
            Flask application.
        """
        self.init_config(app.config)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.Session.remove()

    def create_all(self):
        """Create all tables.

        Returns
        -------
        None
            None.
        """
        self.Model.metadata.create_all(self.engine)

    @property
    def session(self):
        """Get session.

        Returns
        -------
        Session
            Session object.
        """
        session = self.Session()
        return session

    def Column(self, *args, **kwargs):
        return Column(*args, **kwargs)

    @classmethod
    def relationship(cls, *args, **kwargs):
        return relationship(*args, **kwargs)

    @classmethod
    def backref(cls, *args, **kwargs):
        return backref(*args, **kwargs)

    def __getattr__(self, name):
        if hasattr(sa, name):
            return getattr(sa, name)
        raise AttributeError(name)


database = SQLAlchemy(query_class=BaseQuery, model_class=Model)
