""" project admin view """
from flask import flash, url_for, redirect
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, BooleanField, IntegerField
from wtforms.validators import DataRequired

from textflow import auth, services
from textflow.model import Label
from textflow.view.base import FakeBlueprint

__all__ = [
    'LabelsForm',
    'LabelForm'
]

view = FakeBlueprint()


class LabelForm(FlaskForm):
    selected = BooleanField('selected')
    id = StringField('ID')
    label = StringField('Label', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])
    order = IntegerField('Order', validators=[DataRequired()])


class LabelsForm(FlaskForm):
    labels = FieldList(FormField(LabelForm))


@view.route('/projects/<project_id>/dashboard/labels', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def create_label(project_id):
    add_label_form = LabelForm()
    if add_label_form.validate_on_submit():
        lbl = add_label_form.data['label']
        val = add_label_form.data['value']
        order = add_label_form.data['order']
        if services.filter_label(project_id=project_id, value=val) is None:
            obj = Label(value=val, label=lbl, order=order, project_id=project_id)
            services.db.session.add(obj)
            services.db.session.commit()
        else:
            flash('Label with value "{}" exists. Please retry with another value.'.format(val))
    else:
        flash('Invalid form input. Please check and try again. Error: {}'.format(add_label_form.errors))
    return redirect(url_for('dashboard.index', project_id=project_id))


@view.route('/projects/<project_id>/dashboard/labels/update', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def update_labels(project_id):
    labels = services.list_labels(user_id=current_user.id, project_id=project_id)
    labels_form = LabelsForm(labels=labels)
    for label_form in labels_form.labels:
        label_id = label_form.data['id']
        lbl = services.get_label(label_id=label_id)
        label_form.form.populate_obj(lbl)
    services.db.session.commit()
    return redirect(url_for('dashboard.index', project_id=project_id))


@view.route('/projects/<project_id>/dashboard/labels/delete', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def delete_labels(project_id):
    labels = services.list_labels(user_id=current_user.id, project_id=project_id)
    labels_form = LabelsForm(labels=labels)
    none_selected = True
    for ll in labels_form.labels:
        if ll.data['selected']:
            label_id = ll.data['id']
            services.delete_label(label_id)
            none_selected = False
    if none_selected:
        flash('You have to select labels that need to be removed first.')
    return redirect(url_for('dashboard.index', project_id=project_id))
