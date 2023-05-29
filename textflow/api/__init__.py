from fastapi import FastAPI,  APIRouter
from fastapi.middleware.wsgi import WSGIMiddleware

from textflow.api.routes import projects, users, tokens
from textflow.api.db import db

__all__ = [
    'TextFlowAPI'
]

router = APIRouter(
    prefix='/api',
)

router.include_router(tokens.router)
router.include_router(users.router)
router.include_router(projects.router)


class TextFlowAPI(object):
    def __init__(self, prefix=None) -> None:
        self.prefix = prefix

    def init_app(self, app):
        api = FastAPI()
        api.include_router(router)
        self.api = api
        db.set_config(config=app.config)
        db.init_app(api)
        prefix = self.prefix
        if prefix is None:
            prefix = '/'
        self.api.mount(prefix, WSGIMiddleware(app))
