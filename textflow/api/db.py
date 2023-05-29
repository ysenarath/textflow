import contextvars
import typing
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

__all__ = [
    'db',
    'Database',
]


class Database(object):
    def __init__(self):
        self.config: typing.Optional[dict] = None
        self._conn: typing.Optional[Engine] = None

    async def async_session(self) -> typing.AsyncIterable[Session]:
        sess = Session(bind=self._conn)
        try:
            yield sess
        finally:
            sess.close()

    def session(self) -> typing.Iterable[Session]:
        sess = Session(bind=self._conn)
        try:
            yield sess
        finally:
            sess.close()

    def get_engine(self) -> Engine:
        return self._conn

    def open_database_connection_pools(self):
        if self._conn is None:
            self._conn = create_engine(
                self.config["SQLALCHEMY_DATABASE_URI"],
            )

    def close_database_connection_pools(self):
        if self._conn:
            self._conn.dispose()

    def set_config(self, config: typing.Dict):
        self.config = config

    def init_app(self, app):
        app.on_event('startup')(self.open_database_connection_pools)
        app.on_event('shutdown')(self.close_database_connection_pools)

    def __repr__(self):
        return f'<Database {self.url}>'


db: contextvars.ContextVar[Engine] = contextvars.ContextVar('db', default=None)
