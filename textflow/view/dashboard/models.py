import os

import joblib

from flask import jsonify, request, current_app

from textflow import auth, services
from textflow.utils import jsend
from textflow.view.base import FakeBlueprint

view = FakeBlueprint()


@view.route('/api/projects/<project_id>/estimators')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_estimator_names(project_id):
    estimators = services.list_plugin_names(project_id=project_id, plugin_type='estimator')
    return jsonify(jsend.success(estimators))


@view.route('/api/projects/<project_id>/estimators/fit', methods=['POST'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def estimator_fit(project_id):
    resources = current_app.config.get('resources_folder', None)
    if resources is None:
        return jsonify(jsend.fail())
    print(request.json)
    estimator_name = request.json['estimator']
    dataset_name = request.json['dataset']
    version = '0.0.1'
    dataset = services.get_dataset(project_id, dataset_name)
    estimator = services.get_estimator(project_id, estimator_name)
    model = estimator.fit(dataset.X, dataset.y)
    models_fp = os.path.join(resources, 'projects', 'PID_{}'.format(project_id), dataset_name, estimator_name)
    if not os.path.exists(models_fp):
        os.makedirs(models_fp)
    joblib.dump(model, os.path.join(models_fp, 'SKM_v{}.joblib'.format(version)))
    return jsonify(jsend.success(models_fp))


@view.route('/api/projects/<project_id>/models', methods=['POST'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def list_models(project_id):
    return jsonify(jsend.success())
