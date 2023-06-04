from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class TextFlow(object):
    def __init__(self, local_config, url_prefix='/', **kwargs):
        from textflow.api import router as api_router
        from textflow.views import app as views_app
        from textflow.database import db
        db.init_context(local_config)
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
        self.app = FastAPI()
        self.app.mount(url_prefix, app)
