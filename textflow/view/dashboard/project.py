from flask import url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange

from textflow import auth, services
from textflow.view.base import FakeBlueprint

__all__ = [
    'ProjectForm'
]

project_types = [
    ('sequence_labeling', 'Sequence Labeling'),
    ('document_classification', 'Document Classification'),
]

view = FakeBlueprint()


class ProjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    type = SelectField('Type', validators=[DataRequired()], choices=project_types)
    redundancy = IntegerField('Redundancy', validators=[DataRequired(), NumberRange(min=1)])
    guideline_template = TextAreaField('Guideline', validators=[DataRequired()])


@view.route('/projects/<project_id>/dashboard/project', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def post_project(project_id):
    p = services.get_project(user_id=current_user.id, project_id=project_id)
    project_form = ProjectForm(obj=p)
    project_form.populate_obj(p)
    services.db.session.commit()
    return redirect(url_for('dashboard.index', project_id=project_id))
