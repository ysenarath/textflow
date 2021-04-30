""" project admin view """

from flask import jsonify

from textflow import auth, services
from textflow.utils import jsend
from textflow.view.base import FakeBlueprint

view = FakeBlueprint()


@view.route('/api/projects/<project_id>/status')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_status(project_id):
    """Gets agreement scores for provided project

    :param project_id: project id
    :return: multiple types of score values
    """
    status = services.get_status(project_id=project_id)
    return jsonify(jsend.success(status))
