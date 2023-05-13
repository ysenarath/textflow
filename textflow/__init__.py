""" TextFlow """
import logging
from os.path import expanduser

from flask import Flask

from textflow import auth, view, config, services
from textflow.auth import login_manager
from textflow.services.base import database as db

logger = logging.getLogger(__name__)


class TextFlow:
    """ TextFlow """

    def __init__(self, local_config, **kwargs):
        """ Initialize TextFlow

        :param kwargs: configurations
        """
        self.local_config = local_config
        self.app = self._create_app()
        self._init_app()

    def _create_app(self, **kwargs):
        """ Create App

        :return: create flask server
        """
        server = Flask(__name__, static_folder=config.static_folder, template_folder=config.template_folder)
        for bp in view.get_blueprints():
            server.register_blueprint(bp)
        # Add configs to app
        # place to keep project specific resources like images/ models
        server.config['resources_folder'] = expanduser('~/.textflow/')
        server.config['templates'] = {}
        for k, v in self.local_config.items():
            if (k in server.config) and (server.config[k] is not None):
                server.config[k].update(v)
            else:
                server.config[k] = v
        return server

    def _init_app(self):
        """ Initialize App

        :return: initialize flask server
        """
        db.init_app(self.app)
        login_manager.init_app(self.app)

    def app_context(self):
        """ Gets and returns app context from Flask app """
        return self.app.app_context()
