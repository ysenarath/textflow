""" About Page """

from flask import Blueprint

from textflow.view.base import render_template

view = Blueprint('about', __name__)


@view.route('/about')
def index():
    """About page

    :return: rendered about page
    """
    return render_template('about.html')
