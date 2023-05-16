""" project admin view """

from celery.result import AsyncResult
from flask import jsonify

from textflow import auth, services
from textflow.utils import jsend
from textflow.view.base import FakeBlueprint

view = FakeBlueprint()


@view.route('/api/status/projects/<project_id>')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_project_status(project_id):
    """Gets agreement scores for provided project

    :param project_id: project id
    :return: multiple types of score values
    """
    status = services.get_status(project_id=project_id)
    return jsonify(jsend.success(status))


@view.route('/api/status/tasks/<id>')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_task_status(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    status = {
        'ready': result.ready(),
        'successful': result.successful(),
        'value': result.result if result.ready() else None,
    }
    return jsonify(jsend.success(status))
