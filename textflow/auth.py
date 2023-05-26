"""Authentication module.

This module contains the authentication logic for the application.
"""
from flask import abort, flash, g
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)

from textflow.database import queries

__all__ = [
    'login_manager',
    'login_user',
    'login_required',
    'roles_required',
    'logout_user',
    'current_user',
]

login_manager = LoginManager()


def roles_required(role):
    """Check for roles in the assignments.

    :param role: role of the assignment to check
    :return: decorated function
    """

    if not isinstance(role, set):
        if isinstance(role, str):
            role = [role]
        role = set(role)

    def default(func):
        def decorated_func(*args, **kwargs):
            user_id = current_user.id
            if 'project_id' in kwargs:
                project_id = kwargs['project_id']
            elif len(args) > 0:
                project_id = args[0]
            else:
                raise ValueError('No project id provided')
            assignment = queries.get_assignment(
                # user_id, project_id
                user_id=user_id,
                project_id=project_id
            )
            if assignment is None:
                # error that the user is not assigned to the project
                flash(
                    f'You are not assigned to the project with id \
                        \'{project_id}\'', 'error'
                )
                abort(401)
            elif assignment.role in role:
                g.current_user_role = assignment.role
                return func(*args, **kwargs)
            else:
                # error: the user role is not permitted to access the
                # requested resource
                flash('You are not permitted to access the requested \
                      resource', 'error')
                abort(401)

        decorated_func.__name__ = func.__name__
        return decorated_func

    return default
