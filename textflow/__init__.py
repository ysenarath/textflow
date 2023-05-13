""" TextFlow """
import logging
from os.path import expanduser

from flask import Flask, Blueprint

from textflow import view, config
from textflow.auth import login_manager
from textflow.services.base import database as db

logger = logging.getLogger(__name__)


class PrefixMiddleware(object):
    def __init__(self, app, prefix='') -> None:
        super().__init__()
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ['This url does not belong to the app.'.encode()]


class TextFlow:
    """ TextFlow """

    def __init__(self, local_config, **kwargs):
        """ Initialize TextFlow

        :param kwargs: configurations
        """
        self.local_config = local_config
        self.app = self._create_app(**kwargs)
        self._init_app()

    def _create_app(self, url_prefix=None, **kwargs):
        """ Create App

        :return: create flask server
        """
        server = Flask(
            __name__,
            static_folder=config.static_folder,
            template_folder=config.template_folder
        )
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
        if url_prefix is not None:
            server.wsgi_app = PrefixMiddleware(
                server.wsgi_app, prefix=url_prefix
            )
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
