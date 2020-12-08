""" TextFlow """
import logging

from flask import Flask

from textflow import config, view
from textflow.db import db
from textflow.login import login_manager

logger = logging.getLogger(__name__)


class TextFlow:
    """ TextFlow """

    def __init__(self, local_config, **kwargs):
        """ Initialize TextFlow

        :param kwargs: configurations
        """
        self.local_config = local_config
        self.app = self.__create_app()
        self.__init_app()

    def __create_app(self):
        """ Create App

        :return: create flask server
        """
        server = Flask(__name__, static_folder=config.static_folder, template_folder=config.template_folder)
        for bp in view.get_blueprints():
            server.register_blueprint(bp)
        # Add configs to app
        for k, v in self.local_config.items():
            server.config[k] = v
        return server

    def __init_app(self):
        """ Initialize App

        :return: initialize flask server
        """
        db.init_app(self.app)
        login_manager.init_app(self.app)

    def app_context(self):
        """ Gets and returns app context from Flask app """
        return self.app.app_context()
