""" Index view """

from flask import Blueprint, redirect, url_for

from textflow import auth
from textflow.view.base import render_template

view = Blueprint('index', __name__)


@view.route('/', methods=('GET', 'POST'))
def index():
    """Index page

    :return: rendered template
    """
    if auth.current_user.is_authenticated:
        # automatically login to project list page
        return redirect(url_for('project.list_projects'))
    else:

        return render_template('index.html')
