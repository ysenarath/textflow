""" project admin view """
import json

from flask import render_template, Blueprint, jsonify, request, redirect, flash, url_for
from flask_login import current_user
from sklearn.model_selection import train_test_split

from textflow import services, auth
from textflow.metrics.agreement import AgreementScore
from textflow.model import Assignment, Label, Document
from textflow.utils import jsend
from textflow.utils.types import Table
from textflow.view.forms import *

view = Blueprint('dashboard_view', __name__)


@view.route('/projects/<project_id>/dashboard', methods=['GET'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def dashboard(project_id):
    """Get next document for annotation and render that in view

    :return: rendered template
    """
    if current_user.role == 'manager':
        return render_template('dashboard.html', project_id=project_id)
    else:
        p = services.get_project(user_id=current_user.id, project_id=project_id)
        labels = services.list_labels(user_id=current_user.id, project_id=project_id)
        assignments = services.list_assignments(project_id=project_id)
        project_form = ProjectForm(obj=p)
        labels_form = LabelsForm(labels=labels)
        add_label_form = LabelForm()
        users_form = UsersForm(users=assignments)
        add_user_form = AssignmentForm()
        upload_docs_form = UploadForm()
        return render_template('dashboard.html', project_id=project_id,
                               project_form=project_form, labels_form=labels_form, users_form=users_form,
                               add_label_form=add_label_form, add_user_form=add_user_form,
                               upload_docs_form=upload_docs_form)


@view.route('/projects/<project_id>/dashboard', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def post_dashboard(project_id):
    p = services.get_project(user_id=current_user.id, project_id=project_id)
    labels = services.list_labels(user_id=current_user.id, project_id=project_id)
    assignments = services.list_assignments(project_id=project_id)
    project_form = ProjectForm(obj=p)
    labels_form = LabelsForm(labels=labels)
    users_form = UsersForm(users=assignments)
    obj = request.args.get('obj', None)
    action = request.args.get('action', None)
    if action == 'delete':
        if labels_form.validate_on_submit() and obj == 'label':
            none_selected = True
            for ll in labels_form.labels:
                if ll.data['selected']:
                    label_id = ll.data['id']
                    services.delete_label(label_id)
                    none_selected = False
            if none_selected:
                flash('You have to select labels that need to be removed first.')
        elif users_form.validate_on_submit() and obj == 'user':
            none_selected = True
            for u in users_form.users:
                if u.data['selected']:
                    user_id = u.user.data['id']
                    if current_user.id != user_id:
                        services.remove_assignment(user_id, project_id)
                        none_selected = False
                    else:
                        flash('You can\'t remove yourself from the project.')
            if none_selected:
                flash('You have to select users that need to be removed first.')
        return redirect(url_for('dashboard_view.dashboard', project_id=project_id))
    else:
        if project_form.validate_on_submit() and obj == 'project':
            project_form.populate_obj(p)
            services.db.session.commit()
        elif users_form.validate_on_submit() and obj == 'user':
            for u in users_form.users:
                assignment = services.get_assignment(u.user.data['id'], project_id)
                if assignment.role != u.role:
                    assignment.role = u.role.data
            services.db.session.commit()
        elif labels_form.validate_on_submit() and obj == 'label':
            for label_form in labels_form.labels:
                label_id = label_form.data['id']
                lbl = services.get_label(label_id=label_id)
                label_form.form.populate_obj(lbl)
            services.db.session.commit()
    return redirect(url_for('dashboard_view.dashboard', project_id=project_id))


@view.route('/projects/<project_id>/dashboard/label', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def add_label(project_id):
    add_label_form = LabelForm()
    if add_label_form.validate_on_submit():
        lbl = add_label_form.data['label']
        val = add_label_form.data['value']
        if services.filter_label(project_id=project_id, value=val) is None:
            obj = Label(value=val, label=lbl, project_id=project_id)
            services.db.session.add(obj)
            services.db.session.commit()
        else:
            flash('Label with value "{}" exists. Please retry with another value.'.format(val))
    else:
        flash('Invalid form input. Please check and try again. Error: {}'.format(add_label_form.errors))
    return redirect(url_for('dashboard_view.dashboard', project_id=project_id))


@view.route('/projects/<project_id>/dashboard/user', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def add_user(project_id):
    add_user_form = AssignmentForm()
    if add_user_form.validate_on_submit():
        role = add_user_form.data['role']
        username = add_user_form.user.data['username']
        users = services.filter_users(username=username)
        if len(users) == 1:
            user_id = users[0].id
            a = Assignment(user_id=user_id, project_id=project_id, role=role)
            services.db.session.add(a)
            services.db.session.commit()
        else:
            flash('Username not found: "{}". Please enter a valid username.'.format(username))
    else:
        flash('Invalid form input. Please check and try again. Error: {}'.format(add_user_form.errors))
    return redirect(url_for('dashboard_view.dashboard', project_id=project_id))


@view.route('/projects/<project_id>/dashboard/documents', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def upload_documents(project_id):
    upload_docs_form = UploadForm()
    if upload_docs_form.validate_on_submit():
        fp = request.files[upload_docs_form.file.name].stream
        for line in fp:
            d = json.loads(line)
            a = Document(id_str=d['id'], text=d['text'], meta=d['meta'], project_id=project_id)
            services.db.session.add(a)
        services.db.session.commit()
    return redirect(url_for('dashboard_view.dashboard', project_id=project_id))


@view.route('/api/projects/<project_id>/groups')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_group_names(project_id):
    name = request.args.get('name', default='default')
    dataset = services.get_dataset(project_id=project_id, name=name)
    return jsonify(jsend.success(list(dataset.groups_)))


@view.route('/api/projects/<project_id>/datasets')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset_names(project_id):
    return jsonify(jsend.success(services.list_plugin_names(project_id, 'dataset')))


@view.route('/api/projects/<project_id>/datasets/download')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset(project_id):
    dataset = services.get_dataset(project_id=project_id)
    dataset.validator = request.args.get('validator', default=dataset.validator)
    ids = [r.id_str for _, r in dataset.records.items()]
    data = {i: [xs, ys] for i, xs, ys in zip(ids, dataset.X, dataset.y)}
    return jsonify(jsend.success(data))


@view.route('/api/projects/<project_id>/agreement')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_agreement(project_id):
    """Gets agreement scores for provided project

    :param project_id: ident of project
    :return: multiple types of score values
    """
    dataset = services.get_dataset(project_id=project_id)
    # check agreement
    task = AgreementScore(dataset)
    scores = task.kappa()
    return jsonify(jsend.success(scores.to_dict()))


@view.route('/api/projects/<project_id>/models', methods=['GET', 'POST'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_models(project_id):
    if request.method == 'POST':
        dataset = services.get_dataset(project_id, request.json['dataset'])
        model = services.get_model(project_id, request.json['model'])
        try:
            train_X, test_X, train_y, test_y = train_test_split(dataset.X, dataset.y)
            flat_f1 = model.fit(train_X, train_y).score(test_X, test_y)
        except ValueError as err:
            return jsonify(jsend.fail([dict(type='error', title='Error', data=str(err))]))
        scores = Table(['Flat F1 Score'], [['{:.2f}'.format(flat_f1)]])
        return jsonify(jsend.success(scores.to_dict()))
    return jsonify(jsend.success(services.list_plugin_names(project_id, 'model')))
