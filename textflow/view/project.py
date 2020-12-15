""" Project view """
from flask import render_template, Blueprint, request, redirect, url_for
from flask_login import current_user, login_required

from textflow import services

view = Blueprint('project_view', __name__)


@view.route('/projects')
@login_required
def list_projects():
    """ Index page

    :return: rendered template
    """
    projects = services.list_projects(current_user.id)
    return render_template('projects.html', projects=projects)


@view.route('/projects/<project_id>', methods=('GET', 'POST'))
@login_required
def view_project(project_id):
    """ Index page

    :return: rendered template
    """
    try:
        current_page = int(request.args.get('page', default=1))
        if current_page < 1:
            current_page = 1
    except ValueError:
        current_page = 1
    try:
        per_page = int(request.args.get('per_page', default=10))
    except ValueError:
        per_page = 10
    project = services.get_project(current_user.id, project_id)
    if project is None:
        return redirect(url_for('project_view.list_projects'))
    documents = services.list_documents(project_id, current_user.id, paginate=True,
                                        paginate_kwargs={'page': current_page, 'per_page': per_page,
                                                         'error_out': False})
    project_status = services.generate_status_report(user_id=current_user.id, project_id=project.id)
    return render_template('project.html', project=project, project_status=project_status,
                           documents=documents, current_page=current_page, per_page=per_page)
