""" project admin view """
from flask import flash, url_for, redirect
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, BooleanField, SelectField
from wtforms.validators import DataRequired

from textflow import auth, services
from textflow.model import Assignment
from textflow.view.base import FakeBlueprint

__all__ = [
    'UsersForm',
    'AssignmentForm'
]

view = FakeBlueprint()

project_user_roles = [
    ('default', 'Default'),
    ('manager', 'Manager'),
    ('admin', 'Administer'),
]


class UserForm(FlaskForm):
    id = StringField('ID')
    username = StringField('Username', validators=[DataRequired()])


class AssignmentForm(FlaskForm):
    selected = BooleanField('selected')
    user = FormField(UserForm)
    role = SelectField('Role', validators=[DataRequired()], choices=project_user_roles)


class UsersForm(FlaskForm):
    users = FieldList(FormField(AssignmentForm))


@view.route('/projects/<project_id>/dashboard/users', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def create_user(project_id):
    update_user_form = AssignmentForm()
    if update_user_form.validate_on_submit():
        role = update_user_form.data['role']
        username = update_user_form.user.data['username']
        users = services.filter_users(username=username)
        if len(users) == 1:
            user_id = users[0].id
            a = Assignment(user_id=user_id, project_id=project_id, role=role)
            services.db.session.add(a)
            services.db.session.commit()
        else:
            flash('Username not found: "{}". Please enter a valid username.'.format(username))
    else:
        flash('Invalid form input. Please check and try again. Error: {}'.format(update_user_form.errors))
    return redirect(url_for('dashboard.index', project_id=project_id))


@view.route('/projects/<project_id>/dashboard/users/update', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def update_users(project_id):
    assignments = services.list_assignments(project_id=project_id)
    users_form = UsersForm(users=assignments)
    for u in users_form.users:
        assignment = services.get_assignment(u.user.data['id'], project_id)
        if assignment.role != u.role:
            assignment.role = u.role.data
    services.db.session.commit()
    return redirect(url_for('dashboard.index', project_id=project_id))


@view.route('/projects/<project_id>/dashboard/users/delete', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def delete_users(project_id):
    assignments = services.list_assignments(project_id=project_id)
    users_form = UsersForm(users=assignments)
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
    return redirect(url_for('dashboard.index', project_id=project_id))
