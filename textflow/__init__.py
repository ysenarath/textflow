

class TextFlow(object):
    def __init__(self, local_config, url_prefix=None, **kwargs):
        from fastapi import FastAPI
        from textflow.api import router
        from textflow.database import db
        db.init_context(local_config)
        api = FastAPI()
        api.include_router(router)
        self.api = api
