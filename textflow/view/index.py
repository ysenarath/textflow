""" Index view """
from flask import render_template, Blueprint, redirect, url_for
from flask_login import current_user

view = Blueprint('index_view', __name__)


@view.route('/', methods=('GET', 'POST'))
def index():
    """ Index page

    :return: rendered template
    """
    if current_user.is_authenticated:
        # automatically login to project list page
        return redirect(url_for('project_view.list_projects'))
    else:
        return render_template('index.html')
