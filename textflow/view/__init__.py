""" View """

from textflow.view import about, annotate, errors, index, login, project, dashboard

__all__ = [
    about,
    annotate,
    errors,
    index,
    login,
    project,
    dashboard,
]


def get_blueprints():
    """ Get all views

    :return:
    """
    return [about.view, annotate.view, errors.view, index.view, login.view, project.view, dashboard.view]
