"""Database connection and session management.

This module provides a database object that manages database connections and
sessions. This depends on models defined in the models module.

Example
-------
>>> from textflow.database import db
>>> # set database connection valid for the current thread
>>> db.context.set_config(config)
>>> db.create_all()
>>> db.session.add(...)
>>> db.session.commit()
"""
import contextlib
import typing

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Query, Session

from textflow.database.pagination import Pagination, PaginationArgs
from textflow.database.operations import create_user, get_user_by
from textflow.models import mapper_registry as default_mapper_registry
from textflow import schemas


class BaseQuery(Query):
    def paginate(self, page, *, per_page=20, error_out=True):
        """Return `Pagination` instance using already defined query
        parameters.
        """
        if page is None:
            return self.all()
        if isinstance(page, PaginationArgs):
            error_out = page.error_out
            per_page = page.per_page
            page = page.page
        if page < 1:
            if error_out:
                raise IndexError
            page = PaginationArgs.page.default
        if per_page is None:
            per_page = PaginationArgs.per_page.default
        if per_page > PaginationArgs.per_page.le:
            per_page = PaginationArgs.per_page.le
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
        return Pagination(
            page=page,
            per_page=per_page,
            total=total,
            items=items,
        )


class DatabaseContext(object):
    def __init__(self, config) -> None:
        """Update database connection using config provided. Existing ones will
        be overwritten.

        Parameters
        ----------
        uri : str
            Database URI.
        """
        SQLALCHEMY_DATABASE_URL = config['SQLALCHEMY_DATABASE_URI']
        self.engine: Engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        self.Session: sessionmaker = sessionmaker(
            autocommit=False,
            autoflush=True,
            bind=self.engine,
            query_cls=BaseQuery,
        )


class Database(object):
    """Handle database connection and session and keeps track of all models.

    Context variables are used to keep track of the connections for each 
    thread. Fork will create a copy of context variables (at the time of 
    form) for each thread.

    Attributes
    ----------
    mapper_registry : sqlalchemy.orm.registry
    """

    def __init__(self, mapper_registry=None):
        """Initialize database object."""
        if mapper_registry is None:
            # use default mapper registry from models package
            mapper_registry = default_mapper_registry
        self.mapper_registry = mapper_registry

    def init_context(self, config):
        """Initialize database context from config.

        Parameters
        ----------
        config : dict
            Configuration dictionary.

        Returns
        -------
        None
            None.
        """
        self.ctx = DatabaseContext(config)

    @contextlib.contextmanager
    def session(self, *args, **kwargs) -> \
            typing.Generator[Session, None, None]:
        """Get database session from session factory.

        Notes
        -----
        Make sure you have set the database context before calling this
            property.
        This can beused as a Dependency in FastAPI.

        Returns
        -------
        typing.Generator[Session, None, None]
            Database session.
        """
        # call the session factory to get the session
        # this will generate existing session if it is
        # in the thread otherwise, it will create a
        # new session
        if self.ctx.Session is None:
            raise RuntimeError('Database context not initialized. \
                               Use db.init_context(config) \
                               to initialize the context.')
        session = self.ctx.Session()
        try:
            yield session
        finally:
            session.close()

    @property
    def engine(self):
        """Get database engine.

        Returns
        -------
        sqlalchemy.engine.Engine
            Database engine.
        """
        return self.ctx.engine

    def create_all(self):
        """Create all tables.

        Returns
        -------
        None
            None.
        """
        # create database tables
        self.mapper_registry.metadata.create_all(self.engine)
        admin = schemas.User(username='admin', role='admin', password='admin')
        with self.session() as session:
            if get_user_by(session, username=admin.username) is None:
                create_user(session, user=admin)
                print('admin created')
            else:
                print('admin already exists')
        print('database created')


db: Database = Database()
