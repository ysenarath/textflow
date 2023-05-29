"""Views module.

This module contains all the views for the application. Each view is a
blueprint that can be registered with the application.
"""
from textflow.views import (
    about,
    annotate,
    index,
    login,
    dashboard,
    projects,
    users,
)

__all__ = [
    'get_blueprints',
    'about',
    'annotate',
    'index',
    'login',
    'projects',
    'users',
    'dashboard',
]


def get_blueprints():
    return [view.bp for view in [
        about,
        annotate,
        index,
        login,
        projects,
        users,
        dashboard,
    ] if hasattr(view, 'bp')]
