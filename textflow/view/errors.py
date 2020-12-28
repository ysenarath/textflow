""" Errors Page """

from flask import render_template, Blueprint

view = Blueprint('errors_view', __name__)


@view.app_errorhandler(403)
def forbidden(_):
    """forbidden

    :param _:
    :return:
    """
    return render_template('errors/403.html'), 403


@view.app_errorhandler(404)
def page_not_found(_):
    """page_not_found

    :param _:
    :return:
    """
    return render_template('errors/404.html'), 404


@view.app_errorhandler(500)
def internal_server_error(_):
    """internal_server_error

    :param _:
    :return:
    """
    return render_template('errors/500.html'), 500
