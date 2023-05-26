"""Project view."""
from flask import Blueprint, request, redirect, url_for, jsonify

from textflow import auth
from textflow.views.base import render_template, Pagination
from textflow.database import queries
from textflow.utils import jsend

__all__ = [
    'bp',
    'list_projects',
    'view_project',
    'get_project',
    'view_project_history',
]

bp = Blueprint('project', __name__)


@bp.route('/projects')
@auth.login_required
def list_projects():
    """Paginate projects and list them.

    Returns
    -------
    str
        rendered template
    """
    pagination = Pagination()
    projects = queries.list_projects(
        user_id=auth.current_user.id,
        paginate=pagination,
    )
    for p in projects.items:
        assignment = queries.get_assignment(
            user_id=auth.current_user.id,
            project_id=p.id
        )
        p.role = assignment.role
    return render_template(
        'projects.html',
        projects=projects,
        current_page=pagination.page,
        per_page=pagination.per_page,
    )


@bp.route('/projects/<project_id>', methods=('GET', 'POST'))
@auth.login_required
def view_project(project_id):
    """View project.

    Returns
    -------
    str
        Rendered template of project.
    """
    project = queries.get_project(
        user_id=auth.current_user.id,
        project_id=project_id,
    )
    if project is None:
        return redirect(url_for('project.list_projects'))
    flagged = request.args.get('flagged', default=None)
    if flagged is not None:
        flagged = flagged.lower() != 'false'
    project_status = queries.generate_project_report(
        user_id=auth.current_user.id,
        project_id=project.id
    )
    pagination = Pagination()
    return render_template(
        'project.html',
        project=project,
        project_status=project_status,
        flagged=flagged,
        current_page=pagination.page,
        per_page=pagination.per_page,
    )


@bp.route('/api/projects/<project_id>', methods=('GET', 'POST'))
@auth.login_required
def get_project(project_id):
    """API endpoint for getting project.

    Returns
    -------
    str
        JSON response of project.
    """
    project = queries.get_project(
        user_id=auth.current_user.id,
        project_id=project_id,
    )
    if project is None:
        return jsonify(jsend.fail({
            'title': 'Project not found',
            'message': 'Project not found. \
                Please check the project id and try again.',
        }))
    return jsonify(jsend.success(project.to_json()))


@bp.route('/projects/<project_id>/history', methods=('GET', 'POST'))
@auth.login_required
def view_project_history(project_id):
    """View project history.

    Returns
    -------
    str
        Rendered template of project history.
    """
    project = queries.get_project(
        user_id=auth.current_user.id,
        project_id=project_id,
    )
    if project is None:
        return redirect(url_for('project.list_projects'))
    flagged = request.args.get('flagged', default=None)
    if flagged is not None:
        flagged = flagged.lower() != 'false'
    pagination = Pagination()
    documents = queries.list_documents_completed_by_user(
        user_id=auth.current_user.id,
        project_id=project_id,
        flagged=flagged,
        paginate=pagination
    )
    return render_template(
        'history.html',
        project=project,
        documents=documents,
        flagged=flagged,
        current_page=pagination.page,
        per_page=pagination.per_page,
    )
