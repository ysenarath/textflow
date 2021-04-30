""" View """

from textflow.view import about, annotate, index, login, project, user, base, dashboard

__all__ = [
    about,
    annotate,
    index,
    login,
    project,
    user,
    dashboard,
]


def get_blueprints():
    """Get all views

    :return: list of views
    """
    return [about.view, annotate.view, index.view, login.view, project.view, user.view, dashboard.view]
