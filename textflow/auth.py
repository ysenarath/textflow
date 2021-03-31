""" Login related functions """

from flask import abort, flash, g
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from textflow import services

__all__ = [
    'login_manager',
    'login_user',
    'login_required',
    'roles_required',
    'logout_user',
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
                raise ValueError('Project ID argument not found to determine identity of project')
            assignment = services.get_assignment(user_id, project_id)
            if assignment is None:
                flash('Invalid user or project identity', 'error')
                abort(401)
            elif assignment.role in role:
                g.current_user_role = assignment.role
                return func(*args, **kwargs)
            else:
                flash('You are not authorize to access the resource', 'error')
                abort(401)

        decorated_func.__name__ = func.__name__
        return decorated_func

    return default
