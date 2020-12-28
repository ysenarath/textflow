""" project admin view """

from flask import render_template, Blueprint, jsonify, request
from sklearn.model_selection import train_test_split

from textflow import service, auth
from textflow.utils import jsend
from textflow.metrics.agreement import AgreementScore

view = Blueprint('dashboard_view', __name__)


@view.route('/projects/<project_id>/dashboard')
@auth.login_required
@auth.roles_required(role='admin')
def dashboard(project_id):
    """Get next document for annotation and render that in view

    :return: rendered template
    """
    return render_template('dashboard.html', project_id=project_id)


@view.route('/api/projects/<project_id>/datasets')
@auth.login_required
@auth.roles_required(role='admin')
def get_dataset_names(project_id):
    return jsonify(jsend.success(service.list_plugin_names(project_id, 'dataset')))


@view.route('/api/projects/<project_id>/agreement')
@auth.login_required
@auth.roles_required(role='admin')
def get_agreement(project_id):
    """Gets agreement scores for provided project

    :param project_id: ident of project
    :return: multiple types of score values
    """
    dataset = service.get_dataset(project_id=project_id)
    # check agreement
    task = AgreementScore(dataset)
    scores = task.kappa()
    tile_1 = {
        'title': 'Kappa Scores',
        'type': 'table',
        'data': scores.score_table
    }
    tile_2 = {
        'title': 'Average Kappa Score',
        'type': 'value',
        'data': '{:.2f}'.format(scores.avg_score)
    }
    tile_3 = {
        'title': 'Weighted Average Kappa Score',
        'type': 'value',
        'data': '{:.2f}'.format(scores.avg_score)
    }
    return jsonify(jsend.success([tile_1, tile_2, tile_3]))


@view.route('/api/projects/<project_id>/models', methods=['GET', 'POST'])
@auth.login_required
@auth.roles_required(role='admin')
def get_models(project_id):
    if request.method == 'POST':
        dataset = service.get_dataset(project_id, request.json['dataset'])
        model = service.get_model(project_id, request.json['model'])
        train_X, test_X, train_y, test_y = train_test_split(dataset.X, dataset.y)
        flat_f1 = model.fit(train_X, train_y).score(test_X, test_y)
        tile_1 = {
            'title': 'Flat F1 Score',
            'type': 'value',
            'data': '{:.2f}'.format(flat_f1)
        }
        return jsonify(jsend.success([tile_1]))
    return jsonify(jsend.success(service.list_plugin_names(project_id, 'model')))
