"""Index view."""
from flask import Blueprint, redirect, url_for, request

from textflow import auth
from textflow.views.login import LoginForm
from textflow.views.base import render_template

__all__ = [
    'bp',
    'index',
]

bp = Blueprint('index', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    """Index view.

    Returns
    -------
    str
        The rendered template.
    """
    if auth.current_user.is_authenticated:
        # automatically login to project list page
        return redirect(url_for('project.list_projects'))
    else:
        # Here we use a class of some kind to represent and validate our
        # client-side form data. For examp`le, WTForms is a library that will
        # handle this for us, and we use a custom LoginForm to validate.
        login = bool(request.args.get('login', False))
        target = request.args.get('target', None)
        if login and (target is None or not len(target.strip())):
            return redirect(url_for(
                'index.index',
                login=login,
                # get refferer url as target
                target=url_for('index.index'),
            ))
        return render_template(
            'index.html',
            login_form=LoginForm(),
            show_login_form=login,
            target=target
        )
