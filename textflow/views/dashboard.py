from collections import namedtuple
import os
import uuid

import flask
from flask import (
    Blueprint,
    session,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    current_app,
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import (
    StringField,
    IntegerField,
    TextAreaField,
    BooleanField,
    SelectField,
    FileField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired, NumberRange, Regexp

from textflow import auth
from textflow.models import (
    Assignment,
    Label,
    Task,
)
from textflow.database import queries
from textflow.views.base import render_template
from textflow.tasks import shared as st
from textflow.utils import jsend

__all__ = [
    'bp',
]

bp = Blueprint('dashboard', __name__)


class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    redundancy = IntegerField(
        'Redundancy', validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )
    guideline_template = TextAreaField('Guideline', validators=[])


class LabelForm(FlaskForm):
    selected = BooleanField('selected')
    id = StringField('ID')
    label = StringField('Label', validators=[DataRequired()])
    value = StringField('Value', validators=[
        DataRequired(),
        Regexp('^[A-Za-z0-9_-]+$', message='The value must be alphanumeric.')
    ])
    order = IntegerField('Order')
    color = StringField('Color')
    group = StringField('Group')

    class Meta:
        csrf = False  # Disable CSRF


class TaskForm(FlaskForm):
    id = StringField('ID')
    title = StringField('Title', validators=[])
    description = StringField('Description', validators=[])
    condition = StringField('Condition', validators=[])
    labels = FieldList(FormField(LabelForm))


class UserForm(FlaskForm):
    id = StringField('ID')
    username = StringField('Username', validators=[DataRequired()])


class AssignmentForm(FlaskForm):
    selected = BooleanField('selected')
    user = FormField(UserForm)
    role = SelectField(
        'Role',
        validators=[DataRequired()],
        choices=[
            ('default', 'Default'),
            ('manager', 'Manager'),
            ('admin', 'Administer'),
        ]
    )


class UsersForm(FlaskForm):
    users = FieldList(FormField(AssignmentForm))


class FileUploadForm(FlaskForm):
    file = FileField(validators=[
        FileRequired(),
    ])


@bp.route('/projects/<project_id>/dash', methods=['GET'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def index(project_id):
    """Render dashboard.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    flask.Response or str
        Rendered template for dashboard.
    """
    Section = namedtuple('Section', ['label', 'value', 'icon'])
    sidebar = [
        ('General', [
            Section('Status', 'status', 'pie-chart'),
        ]),
        ('Editor', [
            Section('Project', 'project', 'tools'),
            Section('Tasks', 'tasks', 'tags'),
            Section('Users', 'users', 'people'),
            Section('Documents', 'documents', 'file-arrow-up'),
        ])
    ]
    current_section = 'status'
    if ('dash.section' in session) and (project_id in session['dash.section']):
        current_section = session['dash.section'][project_id]
    if auth.current_user.role == 'manager':
        kwargs = dict(project_id=project_id, sidebar=sidebar,
                      section=current_section)
        return render_template('dashboard.html', **kwargs)
    else:
        obj_project = queries.get_project(
            user_id=auth.current_user.id,
            project_id=project_id,
        )
        obj_assignments = queries.list_assignments(project_id=project_id)
        obj_tasks = queries.list_tasks(
            user_id=auth.current_user.id,
            project_id=project_id,
        )
        forms = dict(
            update_project=ProjectForm(obj=obj_project),
            update_tasks=[TaskForm(obj=task) for task in obj_tasks],
            create_task=TaskForm(),
            update_users=UsersForm(users=obj_assignments),
            create_user=AssignmentForm(),
            upload_documents=FileUploadForm(),
        )
        kwargs = dict(
            project_id=project_id,
            sidebar=sidebar,
            forms=forms,
            section=current_section
        )
        return render_template('dashboard/index.html', **kwargs)


@bp.route('/api/projects/<project_id>/dash/sections', methods=['GET'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def update_section(project_id):
    """API endpoint to update section.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    flask.Response or str
        JSON response.
    """
    if 'value' not in flask.request.args:
        return jsonify(jsend.fail({
            'value': 'Argument section \'value\' not defined.'
        }))
    section = flask.request.args['value']
    if 'dash.section' not in session:
        session['dash.section'] = dict()
    session_var = {k: v for k, v in session['dash.section'].items()}
    session_var[project_id] = section
    session['dash.section'] = session_var
    return jsonify(jsend.success(section))


@bp.route('/projects/<project_id>/dash/users', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def create_user(project_id):
    """Create user.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    update_user_form = AssignmentForm()
    if update_user_form.validate_on_submit():
        role = update_user_form.data['role']
        username = update_user_form.user.data['username']
        users = queries.filter_users(username=username)
        if len(users) == 1:
            user_id = users[0].id
            a = Assignment(
                user_id=user_id,
                project_id=project_id,
                role=role
            )
            queries.db.session.add(a)
            queries.db.session.commit()
        else:
            flash(
                f'User with username "{username}" does not exist. \
                      Please retry with another username.'
            )
    else:
        flash('Invalid form input. Please check and try again.')
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route('/projects/<project_id>/dash/users/update', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def update_users(project_id):
    """Update users.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    assignments = queries.list_assignments(project_id=project_id)
    users_form = UsersForm(users=assignments)
    for u in users_form.users:
        assignment = queries.get_assignment(
            user_id=u.user.data['id'],
            project_id=project_id,
        )
        if assignment.role != u.role:
            assignment.role = u.role.data
    queries.db.session.commit()
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route('/projects/<project_id>/dash/users/delete', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def delete_users(project_id):
    """Delete users.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    assignments = queries.list_assignments(project_id=project_id)
    users_form = UsersForm(users=assignments)
    none_selected = True
    for u in users_form.users:
        if u.data['selected']:
            user_id = u.user.data['id']
            if auth.current_user.id != user_id:
                queries.remove_assignment(
                    # user_id, project_id
                    user_id=user_id,
                    project_id=project_id,
                )
                none_selected = False
            else:
                flash('You cannot remove yourself from the project.')
    if none_selected:
        flash('No user selected. Please select at least one user to remove.')
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route('/api/projects/<project_id>/dash/documents', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def upload_documents(project_id):
    """Create a background job to upload documents to a project.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    flask.Response or str
        JSON response.
    """
    upload_docs_form = FileUploadForm()
    if not upload_docs_form.validate_on_submit():
        return jsonify(jsend.fail(upload_docs_form.errors))
    file = request.files[upload_docs_form.file.name]
    upload_filename = str(file.filename)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', None)
    if not os.path.exists(upload_folder) or not os.path.isdir(upload_folder):
        upload_folder = None
    if upload_folder is not None:
        # create a random filename
        filename, ext = os.path.splitext(upload_filename)
        filename = filename + '-' + str(uuid.uuid4()) + ext
        filename = os.path.join(upload_folder, filename)
        file.save(filename)
        content = None
    else:
        filename = upload_filename
        content = file.read().decode('utf-8')
    job = st.upload_documents.delay(
        user_id=auth.current_user.id,
        project_id=project_id,
        filename=filename,
        content=content,
    )
    return jsonify(jsend.success(job.to_dict()))


@bp.route('/api/projects/<project_id>/dash/documents', methods=['DELETE'])
@auth.login_required
@auth.roles_required(role='admin')
def delete_documents(project_id):
    """Create a background job to delete all documents in a project.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    flask.Response or str
        JSON response.
    """
    # from flask_login import current_user
    job = st.delete_documents.delay(
        user_id=auth.current_user.id,
        project_id=project_id
    )
    # return the created job
    return jsonify(jsend.success(job.to_dict()))


@bp.route('/projects/<project_id>/dashboard/tasks', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def create_task(project_id):
    """Create task.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    task_form = TaskForm()
    task = Task(project_id=project_id)
    flash_message = 'Error while creating task. Please check and try again.'
    if task_form.validate_on_submit():
        flash(flash_message)
        return redirect(url_for('dashboard.index', project_id=project_id))
    task.title = task_form.data['title']
    task.description = task_form.data['description']
    task.condition = task_form.data['condition']
    # add label one by one
    successfull = True
    for label_form in task_form.labels:
        if label_form.validate_on_submit():
            successfull = False
            break
        label = label_form.data['label']
        val = label_form.data['value']
        order = label_form.data['order']
        group = None
        if 'group' in label_form.data:
            group = label_form.data['group']
        color = 'random'
        if 'color' in label_form.data:
            color = label_form.data['color']
        obj = queries.filter_label(project_id=project_id, value=val)
        if obj is not None:
            successfull = False
            flash_message = (
                f'Label with value "{val}" already exists. '
                'Please retry with another value.'
            )
            break
        obj = Label(
            value=val, label=label, order=order,
            color=color, group=group
        )
        task.labels.append(obj)
    if successfull:
        try:
            queries.db.session.add(task)
            queries.db.session.commit()
        except Exception:
            queries.db.session.rollback()
            successfull = False
    if not successfull:
        flash(flash_message)
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route(
    '/projects/<project_id>/dashboard/tasks/<task_id>/update',
    methods=['POST']
)
@auth.login_required
@auth.roles_required(role='admin')
def update_task(project_id, task_id):
    """Update task.

    Parameters
    ----------
    project_id : str
        Project id.
    task_id : str
        Task id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    task = queries.get_task(user_id=auth.current_user.id,  task_id=task_id)
    task_form = TaskForm()
    flash_message = 'Error while updating task. Please check and try again.'
    if not task_form.validate_on_submit():
        flash(flash_message)
        return redirect(url_for('dashboard.index', project_id=project_id))
    successfull = True
    if 'title' in task_form.data:
        if task_form.data['title'] == '':
            task.title = None
        else:
            task.title = task_form.data['title']
    if 'description' in task_form.data:
        if task_form.data['description'] == '':
            task.description = None
        else:
            task.description = task_form.data['description']
    if 'condition' in task_form.data:
        if task_form.data['condition'] == '':
            task.condition = None
        else:
            task.condition = task_form.data['condition']
    # update label one by one
    for label_form in task_form.labels:
        if label_form.validate_on_submit():
            label_id = label_form.data['id']
            if label_id is None:
                lbl = Label()
            else:
                lbl = queries.get_label(label_id=label_id)
            label_form.form.populate_obj(lbl)
            if label_id is None:
                task.labels.append(lbl)
        else:
            successfull = False
            break
    else:
        successfull = False
        print(task_form.errors)
    if successfull:
        try:
            queries.db.session.commit()
        except Exception:
            queries.db.session.rollback()
            successfull = False
    if not successfull:
        flash(flash_message)
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route(
    '/projects/<project_id>/dashboard/tasks/<task_id>/delete',
    methods=['POST']
)
@auth.login_required
@auth.roles_required(role='admin')
def delete_task(project_id, task_id):
    """Delete task.

    Parameters
    ----------
    project_id : str
        Project id.
    task_id : str
        Task id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    task = queries.get_task(
        user_id=auth.current_user.id,
        task_id=task_id,
    )
    try:
        queries.db.session.delete(task)
        queries.db.session.commit()
    except Exception:
        queries.db.session.rollback()
        flash('Error while deleting task. Please check and try again.')
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route('/projects/<project_id>/dashboard/labels/delete', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def delete_labels(project_id):
    """Delete labels.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    labels_form = TaskForm()
    none_selected = True
    for ll in labels_form.labels:
        if ll.data['selected']:
            label_id = ll.data['id']
            queries.delete_label(label_id)
            none_selected = False
    if none_selected:
        flash('No labels selected. Please select at \
               least one label to delete.')
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route('/projects/<project_id>/dashboard/project', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def post_project(project_id):
    """Update project.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    redirect
        Redirect to dashboard.
    """
    p = queries.get_project(
        user_id=auth.current_user.id, project_id=project_id)
    project_form = ProjectForm(obj=p)
    if project_form.validate_on_submit():
        project_form.populate_obj(p)
        if p.guideline_template == '':
            flash('The guideline template is empty.', category='warning')
            p.guideline_template = None
        queries.db.session.commit()
    else:
        flash('Invalid form input. Please check and try again.')
    return redirect(url_for('dashboard.index', project_id=project_id))


@bp.route('/api/status/projects/<project_id>')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_project_status(project_id):
    """Gets agreement scores for provided project

    :param project_id: project id
    :return: multiple types of score values
    """
    status = queries.generate_project_report(
        user_id=queries.ignore,
        project_id=project_id,
    )
    return jsonify(jsend.success(status))


@bp.route('/api/status/projects/<project_id>/jobs')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def list_project_jobs(project_id) -> list[str]:
    """List all background jobs for a project.

    Parameters
    ----------
    project_id : str
        Project id.

    Returns
    -------
    flask.Response
        List of job ids.
    """
    user_id = auth.current_user.id
    jobs = []
    for job in queries.list_background_jobs(
        user_id=user_id,
        project_id=project_id
    ):
        jobs.append(job.to_dict())
    return jsonify(jsend.success(jobs))


@bp.route('/api/status/projects/<project_id>/jobs/<job_id>')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_job_status(project_id, job_id: str) -> dict[str, object]:
    job = queries.get_job(
        user_id=auth.current_user.id,
        project_id=project_id,
        job_id=job_id
    )
    if job is None:
        return jsonify(jsend.fail({
            'job_id': f'Job with id {job_id} does not exist \
                for project {project_id}.',
        }))
    # result = None
    # status = {
    #     'ready': result.ready(),
    #     'successful': result.successful(),
    #     'value': result.result if result.ready() else None,
    # }
    status = {}
    return jsonify(jsend.success(status))
