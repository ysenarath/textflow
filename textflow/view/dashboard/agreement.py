""" project admin view """

from flask import jsonify

from textflow import auth, services
from textflow.metrics.agreement import AgreementScore
from textflow.utils import jsend
from textflow.view.base import FakeBlueprint

view = FakeBlueprint()


@view.route('/api/projects/<project_id>/agreement')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_agreement(project_id):
    """Gets agreement scores for provided project

    :param project_id: project id
    :return: multiple types of score values
    """
    dataset = services.get_dataset(project_id=project_id)
    # check agreement
    task = AgreementScore(dataset)
    scores = task.kappa()
    return jsonify(jsend.success(scores.to_dict()))
