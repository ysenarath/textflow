"""TextFlow

This module contains the main entry point to TextFlow. It is responsible for
creating the Flask app and initializing the database. It also contains the
command line interface for TextFlow.
"""
import logging
import os
from os.path import expanduser


from flask import Flask

from textflow import config, jobs, views
from textflow.database import db
from textflow.auth import login_manager
from textflow.api import TextFlowAPI

logger = logging.getLogger(__name__)

__all__ = [
    'TextFlowAPI',
    'TextFlowWeb'
]


class TextFlow:
    def __init__(self, local_config, **kwargs):
        self.local_config = local_config
        self.app = self._create_app(**kwargs)
        db.init_app(self.app)
        login_manager.init_app(self.app)
        self.celery_app = jobs.init_app(self.app)

    def _create_app(self, url_prefix=None, **kwargs):
        app = Flask(
            __name__,
            static_folder=config.static_folder,
            template_folder=config.template_folder
        )
        for bp in views.get_blueprints():
            app.register_blueprint(bp)
        # shared folder for keeping non deployment specific files
        # make sure you use a random name for each files
        shared = expanduser('~/.textflow/')
        app.config['RESOURCES_FOLDER'] = shared
        app.config['UPLOAD_FOLDER'] = os.path.join(shared, 'uploads')
        app.config['TEMPLATES'] = {}
        for k, v in self.local_config.items():
            if (k in app.config) and (app.config[k] is not None):
                app.config[k].update(v)
            else:
                app.config[k] = v
        self.api = TextFlowAPI(url_prefix)
        self.api.init_app(app)
        return app

    def app_context(self):
        """Returns a context for the app."""
        return self.app.app_context()
