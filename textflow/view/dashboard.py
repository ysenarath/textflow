""" project admin view """

import json

from flask import render_template, Blueprint, jsonify, request
from sklearn.model_selection import train_test_split

from textflow import service, auth
from textflow.utils import jsend
from textflow.metrics.agreement import AgreementScore
from textflow.utils.types import Table

view = Blueprint('dashboard_view', __name__)


@view.route('/projects/<project_id>/dashboard')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def dashboard(project_id):
    """Get next document for annotation and render that in view

    :return: rendered template
    """
    return render_template('dashboard.html', project_id=project_id)


@view.route('/api/projects/<project_id>/groups')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_group_names(project_id):
    name = request.args.get('name', default='default')
    dataset = service.get_dataset(project_id=project_id, name=name)
    return jsonify(jsend.success(list(dataset.groups_)))


@view.route('/api/projects/<project_id>/datasets')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset_names(project_id):
    return jsonify(jsend.success(service.list_plugin_names(project_id, 'dataset')))


@view.route('/api/projects/<project_id>/datasets/download')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset(project_id):
    dataset = service.get_dataset(project_id=project_id)
    dataset.validator = request.args.get('validator', default=dataset.validator)
    ids = [r.id_str for _, r in dataset.records.items()]
    data = {i: [xs, ys] for i, xs, ys in zip(ids, dataset.X, dataset.y)}
    return jsonify(jsend.success(data))


@view.route('/api/projects/<project_id>/agreement')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_agreement(project_id):
    """Gets agreement scores for provided project

    :param project_id: ident of project
    :return: multiple types of score values
    """
    dataset = service.get_dataset(project_id=project_id)
    # check agreement
    task = AgreementScore(dataset)
    scores = task.kappa()
    return jsonify(jsend.success(scores.to_dict()))


@view.route('/api/projects/<project_id>/models', methods=['GET', 'POST'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_models(project_id):
    if request.method == 'POST':
        dataset = service.get_dataset(project_id, request.json['dataset'])
        model = service.get_model(project_id, request.json['model'])
        try:
            train_X, test_X, train_y, test_y = train_test_split(dataset.X, dataset.y)
            flat_f1 = model.fit(train_X, train_y).score(test_X, test_y)
        except ValueError as err:
            return jsonify(jsend.fail([dict(type='error', title='Error', data=str(err))]))
        scores = Table(['Flat F1 Score'], [['{:.2f}'.format(flat_f1)]])
        return jsonify(jsend.success(scores.to_dict()))
    return jsonify(jsend.success(service.list_plugin_names(project_id, 'model')))
