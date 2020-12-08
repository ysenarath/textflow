""" annotation view """
import json

from flask import redirect, url_for, render_template, request, jsonify, Blueprint
from flask_login import login_required, current_user

from textflow import services
from textflow.utils import jsend

view = Blueprint('annotate_view', __name__)


@view.route('/projects/<project_id>/annotate')
@login_required
def annotate_next(project_id):
    """ Get next document for annotation and render that in view

    :return: rendered template
    """
    project = services.get_project(current_user.id, project_id)
    document = services.next_document(current_user.id, project_id)
    if document is None:
        return render_template('annotate.html', project=project, document=document)
    return redirect(url_for('annotate_view.annotate', project_id=project_id, document_id=document.id))


@view.route('/projects/<project_id>/annotate/<document_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def annotate(project_id, document_id):
    """ Annotate document with provided ID.

    :param project_id: project id
    :param document_id: document id
    :return: rendered template
    """
    document_id = str(document_id)
    user_id = current_user.id
    if request.method == 'DELETE':
        annotation_id = request.json['data']['id']
        status = services.delete_annotation(current_user.id, project_id, annotation_id)
        if not status:
            return jsonify(jsend.fail({'title': 'Delete failed.', 'body': 'Annotation not found.'}))
        return jsonify(jsend.success({'title': 'Delete success.', 'body': 'Successfully deleted annotation.'}))
    elif request.method == 'POST':
        if 'data' in request.json and request.json['type'] == 'annotation':
            annotation = request.json['data']
            annotation_id, label_value = annotation['id'], annotation['label']
            annotation_span = dict(start=annotation['span']['start'], length=annotation['span']['length'])
            # update annotation if exists
            data = {'label': {'value': label_value}, 'span': annotation_span}
            status = services.update_annotation(project_id, current_user.id, annotation_id, data)
            # if updating fails add the annotation
            if not status:
                services.add_annotation(project_id, user_id, document_id, data)
        elif 'data' in request.json:
            label_value = request.json['data']['value']
            label_status = request.json['data']['status']
            if label_status:
                # add to labels
                annotations = services.filter_annotations_by_label(user_id, project_id, document_id, label_value)
                if len(annotations) == 0:
                    annotation = dict(label=dict(value=label_value))
                    status = services.add_annotation(project_id, current_user.id, document_id, annotation)
                else:
                    return jsonify(jsend.fail({'title': 'Object not found.', 'body': 'Invalid operation request.'}))
            else:
                # delete from labels
                annotations = services.filter_annotations_by_label(user_id, project_id, document_id, label_value)
                status = services.delete_annotation(user_id, project_id, annotations[0].id)
        else:
            status = services.update_annotation_set(user_id, document_id, completed=True)
        return jsonify(jsend.success({'title': 'Update success.', 'body': 'Successfully updated annotation.'}))
    else:
        document = services.get_document(user_id, project_id, document_id)
        project = services.get_project(user_id, project_id)
        options = json.dumps([{'value': label.value, 'label': label.label} for label in project.labels])
        annotation_set = services.get_annotation_set(user_id, project_id, document_id)
        annotations = []
        if annotation_set is not None and project.type == 'sequence_labeling':
            for a in annotation_set.annotations:
                annotations.append({
                    'id': a.id,
                    'label': a.label.value,
                    'span': {
                        'start': a.span.start,
                        'length': a.span.length,
                    },
                })
        return render_template('annotate.html', project=project, document=document,
                               annotation_set=annotation_set, options=options, annotations=json.dumps(annotations))
