from flask import Blueprint

from textflow.views.base import render_template

bp = Blueprint('about', __name__)

__all__ = [
    'bp',
    'about',
]


@bp.route('/about')
def about():
    """About view.

    Returns
    -------
    str
        The rendered template.
    """
    return render_template('about.html')
