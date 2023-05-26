"""Views module.

This module contains all the views for the application. Each view is a
blueprint that can be registered with the application.
"""
from textflow.views import (
    about,
    annotate,
    index,
    login,
    project,
    user,
    dashboard,
)

__all__ = [
    'get_blueprints',
    'about',
    'annotate',
    'index',
    'login',
    'project',
    'user',
    'dashboard',
]


def get_blueprints():
    return [view.bp for view in [
        about,
        annotate,
        index,
        login,
        project,
        user,
        dashboard,
    ] if hasattr(view, 'bp')]
