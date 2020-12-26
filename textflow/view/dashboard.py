""" project admin view """

from flask import redirect, url_for, render_template, Blueprint, flash
from flask_login import login_required, current_user

from textflow import services
from textflow.metrics.agreement import AgreementScore

view = Blueprint('dashboard_view', __name__)


@view.route('/projects/<project_id>/dash')
@view.route('/projects/<project_id>/dashboard')
@login_required
def dashboard(project_id):
    """ Get next document for annotation and render that in view

    :return: rendered template
    """
    user_id = current_user.id
    assignment = services.get_assignment(user_id, project_id)
    if assignment.role == 'admin':
        dataset = services.get_dataset(project_id=1)
        task = AgreementScore(dataset)
        avg_score, table = task.kappa(return_table=True)
        section_1 = {
            'title': 'Kappa Scores',
            'type': 'table',
            'data': table
        }
        section_2 = {
            'title': 'Average Kappa Score',
            'type': 'value',
            'data': avg_score
        }
        return render_template('dashboard.html', sections=[
            section_1,
            section_2
        ])
    else:
        flash('Please login as admin to view dashboard', 'error')
    return redirect(url_for('project_view.view_project', project_id=project_id))
