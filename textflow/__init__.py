from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from textflow.api import router as api_router
from textflow.views import app as views_app


class TextFlow(object):
    def __init__(self, local_config, url_prefix='/', **kwargs):
        from textflow.database import db
        db.init_context(local_config)
        self.url_prefix = url_prefix

    def create_app(self):
        if not hasattr(self, '_app'):
            app = FastAPI()
            app.add_middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            app.include_router(api_router)
            app.mount('/', views_app)
            self._app = FastAPI()
            self._app.mount(self.url_prefix, app)
        return self._app
