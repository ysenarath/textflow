# Copyright 2021 by Yasas Senarath.
# All rights reserved.
# This file is part of the TextFlow,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections import namedtuple

from flask import Blueprint, request
from flask_login import current_user

from textflow import services, auth
from textflow.view.base import render_template
from textflow.view.dashboard.documents import UploadForm
from textflow.view.dashboard.labels import LabelsForm, LabelForm
from textflow.view.dashboard.project import ProjectForm
from textflow.view.dashboard.users import UsersForm, AssignmentForm
from textflow.view.dashboard import agreement, status, dataset, project, labels, models

__all__ = [
    'view'
]

view = Blueprint('dashboard', __name__)


@view.route('/projects/<project_id>/dashboard', methods=['GET'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def index(project_id):
    """Render dashboard

    :param project_id: project id
    :return: rendered template for dashboard
    """
    Section = namedtuple('Section', ['label', 'value', 'icon'])
    sidebar = [
        ('General', [
            Section('Status', 'status', 'fa-tasks'),
            Section('Agreement', 'agreement', 'fa-chart-bar'),
            Section('Dataset', 'dataset', 'fa-table'),
            Section('Models', 'models', 'fa-magic'),
        ]),
        ('Editor', [
            Section('Project', 'project', 'fa-tools'),
            Section('Labels', 'labels', 'fa-tags'),
            Section('Users', 'users', 'fa-users'),
            Section('Documents', 'documents', 'fa-file-alt'),
        ])
    ]
    current_section = request.args.get('section', 'status')
    if current_user.role == 'manager':
        kwargs = dict(project_id=project_id, sidebar=sidebar, section=current_section)
        return render_template('dashboard/index.html', **kwargs)
    else:
        obj_project = services.get_project(user_id=current_user.id, project_id=project_id)
        obj_assignments = services.list_assignments(project_id=project_id)
        obj_labels = services.list_labels(user_id=current_user.id, project_id=project_id)
        forms = dict(
            update_project=ProjectForm(obj=obj_project),
            update_labels=LabelsForm(labels=obj_labels),
            create_label=LabelForm(),
            update_users=UsersForm(users=obj_assignments),
            create_user=AssignmentForm(),
            upload_documents=UploadForm(),
        )
        kwargs = dict(project_id=project_id, sidebar=sidebar, forms=forms, section=current_section)
        return render_template('dashboard/index.html', **kwargs)


agreement.view.register(view)
status.view.register(view)
dataset.view.register(view)
models.view.register(view)
project.view.register(view)
labels.view.register(view)
users.view.register(view)
documents.view.register(view)
