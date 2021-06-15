""" project admin view """

from flask import jsonify, request

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
    if 'blacklist' in request.args:
        blacklist = request.args.getlist('blacklist')
    else:
        blacklist = []
    dataset = services.get_dataset(project_id=project_id)
    # check agreement
    task = AgreementScore(dataset, blacklist=blacklist)
    scores = [
        {
            'label': 'Kappa Agreement',
            'table': task.kappa().to_dict(orient='split')
        },
        {
            'label': 'Percentage Agreement',
            'table': task.percentage().to_dict(orient='split')
        },
    ]
    return jsonify(jsend.success(scores))
