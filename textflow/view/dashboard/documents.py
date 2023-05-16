import json

from celery import shared_task

from flask import request, flash, jsonify

from flask_login import current_user

from flask_wtf import FlaskForm
from wtforms import FileField
from flask_wtf.file import FileRequired

import pandas as pd

from textflow import auth, services
from textflow.model import Document, Task
from textflow.view.base import FakeBlueprint
from textflow.utils import jsend

__all__ = [
    'UploadForm',
]

view = FakeBlueprint()


class UploadForm(FlaskForm):
    file = FileField(validators=[
        FileRequired(),
    ])


@view.route('/api/projects/<project_id>/dashboard/documents', methods=['POST'])
@auth.login_required
@auth.roles_required(role='admin')
def upload_documents(project_id):
    upload_docs_form = UploadForm()
    if upload_docs_form.validate_on_submit():
        file = request.files[upload_docs_form.file.name]
        filename = str(file.filename)
        # when buffer is a csv file
        if filename.endswith('.csv'):
            # todo: create a generator from the stream to avoid loading the
            # whole file into memory
            data = pd.read_csv(file.stream).to_dict(orient='records')
        elif filename.endswith('.jsonl'):
            # create a generator to avoid loading the whole file into memory
            data = (json.loads(line) for line in file.stream)
        else:
            flash(
                f'Tried to upload a file with an unknown extension: {filename}',
                'error'
            )
        is_valid = True
        for i, d in enumerate(data):
            if not isinstance(d, dict):
                flash(
                    f'Tried to upload a file with an unknown format: {filename}',
                    'error'
                )
                is_valid = False
                break
            elif 'id' not in d and 'ID' not in d and 'Id' not in d:
                # message that the id is missing
                flash(
                    f'ID field is missing in {filename} at line {i}', 'error')
                is_valid = False
                break
            elif 'text' not in d and 'TEXT' not in d and 'Text' not in d:
                # message that the text is missing
                flash(
                    f'Text field is missing in {filename} at line {i}', 'error')
                is_valid = False
                break
            document = Document(
                # get source_id from id, ID or Id
                source_id=d.get('id', d.get('ID', d.get('Id'))),
                # get text from text, TEXT or Text
                text=d.get('text', d.get('TEXT', d.get('Text'))),
                meta=d,
                project_id=project_id
            )
            services.db.session.add(document)
        if is_valid:
            services.db.session.commit()
            return jsonify(jsend.success({
                'title': 'Documents added',
                'message': 'Documents added successfully',
            }))
        else:
            services.db.session.rollback()
    return jsonify(jsend.fail({
        'title': 'Documents not added',
        'message': 'Documents were not added',
    }))


@shared_task(ignore_result=False)
def delete_documents_task(user_id, project_id) -> int:
    services.delete_documents(user_id, project_id)


@view.route('/api/projects/<project_id>/dashboard/documents', methods=['DELETE'])
@auth.login_required
@auth.roles_required(role='admin')
def delete_documents(project_id):
    # from flask_login import current_user
    user_id = current_user.id
    task_hash = f'delete_documents({user_id},{project_id})'
    result = delete_documents_task.delay(user_id, project_id)
    task = Task(
        task_id=result.id,
        hash=task_hash,
        user_id=user_id,
    )
    services.db.session.add(task)
    services.db.session.commit()
    return jsonify(jsend.success({
        'title': 'Scheduled documents deletion',
        'message': 'Documents deletion scheduled successfully',
        'task_id': result.id,
    }))
