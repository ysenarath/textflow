"""Scripts related to dataset generation"""

from flask import jsonify, request

from textflow import auth, services
from textflow.utils import jsend
from textflow.view.base import FakeBlueprint

view = FakeBlueprint()


@view.route('/api/projects/<project_id>/groups')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_group_names(project_id):
    name = request.args.get('name', default='default')
    dataset = services.get_dataset(project_id=project_id, name=name)
    return jsonify(jsend.success(list(dataset.groups_)))


@view.route('/api/projects/<project_id>/datasets')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset_names(project_id):
    return jsonify(jsend.success(services.list_plugin_names(project_id=project_id, plugin_type='dataset')))


@view.route('/api/projects/<project_id>/datasets/download')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset(project_id):
    dataset = services.get_dataset(project_id=project_id)
    dataset.validator = request.args.get('validator', default=dataset.validator)
    ids = [r.id_str for _, r in dataset.records.items()]
    data = {i: [xs, ys] for i, xs, ys in zip(ids, dataset.X, dataset.y)}
    return jsonify(jsend.success(data))
