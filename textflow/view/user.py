from flask import Blueprint, request, jsonify
from flask_login import current_user

from textflow import auth, services

view = Blueprint('user_view', __name__)


@view.route('/api/user', methods=['POST'])
@auth.login_required
def update_user():
    """User update route

    :return: action status
    """
    if 'data' in request.json:
        data = request.json['data']
        if ('profile' in data) and ('theme' in data['profile']):
            current_user.profile.theme = data['profile']['theme']
        services.db.session.commit()
    return jsonify({
        'status': 'success',
        'message': 'User profile updated successfully.'
    })
