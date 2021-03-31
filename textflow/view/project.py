""" Project view """
from flask import render_template, Blueprint, request, redirect, url_for

from textflow import services, auth

view = Blueprint('project_view', __name__)


def paginate_kwargs():
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
    return {'page': current_page, 'per_page': per_page, 'error_out': False}


@view.route('/projects')
@auth.login_required
def list_projects():
    """List projects

    :return: rendered template
    """
    pag = paginate_kwargs()
    projects = services.list_projects(auth.current_user.id, paginate=True, paginate_kwargs=pag)
    for p in projects.items:
        assignment = services.get_assignment(auth.current_user.id, p.id)
        p.role = assignment.role
    return render_template('projects.html', projects=projects, current_page=pag['page'], per_page=pag['per_page'])


@view.route('/projects/<project_id>', methods=('GET', 'POST'))
@auth.login_required
def view_project(project_id):
    """View project

    :return: rendered template
    """
    project = services.get_project(auth.current_user.id, project_id)
    if project is None:
        return redirect(url_for('project_view.list_projects'))
    pag = paginate_kwargs()
    flagged = request.args.get('flagged', default=None)
    if flagged is not None:
        flagged = flagged.lower() != 'false'
    project_status = services.generate_status_report(user_id=auth.current_user.id, project_id=project.id)
    return render_template('project.html', project=project, project_status=project_status,
                           flagged=flagged, current_page=pag['page'], per_page=pag['per_page'])


@view.route('/projects/<project_id>/history', methods=('GET', 'POST'))
@auth.login_required
def view_project_history(project_id):
    """View project

    :return: rendered template
    """
    project = services.get_project(auth.current_user.id, project_id)
    if project is None:
        return redirect(url_for('project_view.list_projects'))
    pag = paginate_kwargs()
    flagged = request.args.get('flagged', default=None)
    if flagged is not None:
        flagged = flagged.lower() != 'false'
    documents = services.list_documents(project_id, auth.current_user.id, flagged=flagged,
                                        paginate=True, paginate_kwargs=pag)
    return render_template('history.html', project=project, documents=documents, flagged=flagged,
                           current_page=pag['page'], per_page=pag['per_page'])
