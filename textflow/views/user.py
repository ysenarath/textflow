from flask import Blueprint, request, jsonify
from flask_login import current_user

from textflow import auth
from textflow.database import queries

bp = Blueprint('user', __name__)

__all__ = [
    'bp',
    'update_user',
]


@bp.route('/api/user', methods=['POST'])
@auth.login_required
def update_user():
    """API endpoint to update user.

    Returns
    -------
    str
        Action status.
    """
    if 'data' in request.json:
        data = request.json['data']
        if ('profile' in data) and ('theme' in data['profile']):
            current_user.profile.theme = data['profile']['theme']
        queries.db.session.commit()
    return jsonify({
        'status': 'success',
        'message': 'User updated successfully.'
    })
