""" Index view """
from flask import render_template, Blueprint

view = Blueprint('index_view', __name__)


@view.route('/', methods=('GET', 'POST'))
def index():
    """ Index page

    :return: rendered template
    """
    return render_template('index.html')
