""" project admin view """

from flask import render_template, Blueprint, jsonify, request, redirect, flash, url_for
from flask_login import current_user
from sklearn.model_selection import train_test_split

from textflow import service, auth
from textflow.metrics.agreement import AgreementScore
from textflow.utils import jsend
from textflow.utils.types import Table
from textflow.view.forms import UsersForm, LabelsForm, ProjectForm, LabelForm, AssignmentForm

view = Blueprint('dashboard_view', __name__)


@view.route('/projects/<project_id>/dashboard', methods=['GET', 'POST'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def dashboard(project_id):
    """Get next document for annotation and render that in view

    :return: rendered template
    """
    project = service.get_project(user_id=current_user.id, project_id=project_id)
    labels = service.list_labels(user_id=current_user.id, project_id=project_id)
    assignments = service.list_assignments(project_id=project_id)
    project_form = ProjectForm(obj=project)
    labels_form = LabelsForm(labels=labels)
    add_label_form = LabelForm()
    users_form = UsersForm(users=assignments)
    add_user_form = AssignmentForm()
    obj = request.args.get('obj', None)
    action = request.args.get('action', None)
    if request.method == 'POST' and action == 'delete':
        if labels_form.validate_on_submit() and obj == 'label':
            none_selected = True
            for ll in labels_form.labels:
                if ll.data['selected']:
                    label_id = ll.data['id']
                    service.delete_label(label_id)
                    none_selected = False
            if none_selected:
                flash('You have to select labels that need to be removed first.')
        elif users_form.validate_on_submit() and obj == 'user':
            none_selected = True
            for u in users_form.users:
                if u.data['selected']:
                    user_id = u.user.data['id']
                    if current_user.id != user_id:
                        service.remove_assignment(user_id, project_id)
                        none_selected = False
                    else:
                        flash('You can\'t remove yourself from the project.')
            if none_selected:
                flash('You have to select users that need to be removed first.')
        return redirect(url_for('dashboard_view.dashboard', project_id=project_id))
    elif request.method == 'POST':
        if project_form.validate_on_submit() and obj == 'project':
            project_form.populate_obj(project)
            service.commit()
        elif users_form.validate_on_submit() and obj == 'user':
            for u in users_form.users:
                assignment = service.get_assignment(u.user.data['id'], project_id)
                if assignment.role != u.role:
                    assignment.role = u.role.data
            service.commit()
        elif labels_form.validate_on_submit() and obj == 'label':
            for label_form in labels_form.labels:
                label_id = label_form.data['id']
                label = service.get_label(label_id=label_id)
                label_form.form.populate_obj(label)
            service.commit()
        return redirect(url_for('dashboard_view.dashboard', project_id=project_id))
    return render_template('dashboard.html', project_id=project_id,
                           project_form=project_form, labels_form=labels_form, users_form=users_form,
                           add_label_form=add_label_form, add_user_form=add_user_form)


@view.route('/api/projects/<project_id>/groups')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_group_names(project_id):
    name = request.args.get('name', default='default')
    dataset = service.get_dataset(project_id=project_id, name=name)
    return jsonify(jsend.success(list(dataset.groups_)))


@view.route('/api/projects/<project_id>/datasets')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset_names(project_id):
    return jsonify(jsend.success(service.list_plugin_names(project_id, 'dataset')))


@view.route('/api/projects/<project_id>/datasets/download')
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_dataset(project_id):
    dataset = service.get_dataset(project_id=project_id)
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
    dataset = service.get_dataset(project_id=project_id)
    # check agreement
    task = AgreementScore(dataset)
    scores = task.kappa()
    return jsonify(jsend.success(scores.to_dict()))


@view.route('/api/projects/<project_id>/models', methods=['GET', 'POST'])
@auth.login_required
@auth.roles_required(role=['admin', 'manager'])
def get_models(project_id):
    if request.method == 'POST':
        dataset = service.get_dataset(project_id, request.json['dataset'])
        model = service.get_model(project_id, request.json['model'])
        try:
            train_X, test_X, train_y, test_y = train_test_split(dataset.X, dataset.y)
            flat_f1 = model.fit(train_X, train_y).score(test_X, test_y)
        except ValueError as err:
            return jsonify(jsend.fail([dict(type='error', title='Error', data=str(err))]))
        scores = Table(['Flat F1 Score'], [['{:.2f}'.format(flat_f1)]])
        return jsonify(jsend.success(scores.to_dict()))
    return jsonify(jsend.success(service.list_plugin_names(project_id, 'model')))
