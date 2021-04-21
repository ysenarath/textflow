""" About Page """

from flask import Blueprint

from textflow.view.base import render_template

view = Blueprint('about_view', __name__)


@view.route('/about')
def about():
    """About page

    :return: rendered about page
    """
    return render_template('about.html')
