import json

from flask import request, redirect, url_for

from flask_wtf import FlaskForm
from wtforms import FileField

from textflow import auth, services
from textflow.model import Document
from textflow.view.base import FakeBlueprint

__all__ = [
    'UploadForm',
]

view = FakeBlueprint()


class UploadForm(FlaskForm):
    file = FileField()


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
    return redirect(url_for('dashboard.index', project_id=project_id))
