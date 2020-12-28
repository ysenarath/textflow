""" About Page """

from flask import render_template, Blueprint

view = Blueprint('about_view', __name__)


@view.route('/about')
def about():
    """About page

    :return: rendered about page
    """
    return render_template('about.html')
