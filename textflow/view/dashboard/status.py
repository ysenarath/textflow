""" project admin view """

from celery.result import AsyncResult
from flask import jsonify
from flask_login import current_user

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


@view.route('/api/status/projects/<project_id>/tasks')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def list_project_tasks(project_id) -> list[str]:
    user_id = current_user.id
    tasks = []
    for task in services.list_tasks(user_id=user_id, project_id=project_id):
        tasks.append({
            'id': task.id,
            'user_id': task.user_id,
            'project_id': task.project_id,
        })
    return jsonify(jsend.success(tasks))


@view.route('/api/status/projects/<project_id>/tasks/<task_id>')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_task_status(project_id, task_id: str) -> dict[str, object]:
    task = services.get_task(
        user_id=current_user.id,
        project_id=project_id,
        task_id=task_id
    )
    if task is None:
        return jsonify(jsend.error({
            'title': 'Task not found',
            'message': f'Task with id \'{task_id}\' does not exist',
        }))
    result = AsyncResult(task_id)
    status = {
        'ready': result.ready(),
        'successful': result.successful(),
        'value': result.result if result.ready() else None,
    }
    return jsonify(jsend.success(status))
