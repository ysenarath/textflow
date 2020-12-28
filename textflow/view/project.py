""" Project view """
from flask import render_template, Blueprint, request, redirect, url_for

from textflow import service, auth

view = Blueprint('project_view', __name__)


@view.route('/projects')
@auth.login_required
def list_projects():
    """List projects

    :return: rendered template
    """
    projects = service.list_projects(auth.current_user.id)
    for p in projects:
        assignment = service.get_assignment(auth.current_user.id, p.id)
        p.role = assignment.role
    return render_template('projects.html', projects=projects)


@view.route('/projects/<project_id>', methods=('GET', 'POST'))
@auth.login_required
def view_project(project_id):
    """View project

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
    project = service.get_project(auth.current_user.id, project_id)
    if project is None:
        return redirect(url_for('project_view.list_projects'))
    paginate_kwargs = {'page': current_page, 'per_page': per_page, 'error_out': False}
    documents = service.list_documents(project_id, auth.current_user.id, paginate=True,
                                       paginate_kwargs=paginate_kwargs)
    project_status = service.generate_status_report(user_id=auth.current_user.id, project_id=project.id)
    return render_template('project.html', project=project, project_status=project_status, documents=documents,
                           current_page=current_page, per_page=per_page)
