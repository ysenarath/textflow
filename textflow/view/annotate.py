""" annotation view """
import json

from flask import redirect, url_for, request, jsonify, Blueprint

from textflow import services, auth
from textflow.view.base import render_template
from textflow.utils import jsend

view = Blueprint('annotate', __name__)


@view.route('/projects/<project_id>/annotate')
@auth.login_required
def annotate_next(project_id):
    """Get next document for annotation and render that in view

    :return: rendered template
    """
    current_user = auth.current_user
    project = services.get_project(current_user.id, project_id)
    if project is None:
        return redirect(url_for('project.list_projects'))
    document = services.next_document(current_user.id, project_id)
    if document is None:
        return render_template('annotate.html', project=project)
    return redirect(url_for('annotate.annotate', project_id=project_id, document_id=document.id))


@view.route('/projects/<project_id>/documents/<document_id>/annotate')
@auth.login_required
def annotate(project_id, document_id):
    """Annotate document with provided ID.

    :param project_id: project id
    :param document_id: document id
    :return: rendered template
    """
    current_user = auth.current_user
    document_id = str(document_id)
    project = services.get_project(current_user.id, project_id)
    if project is None:
        return redirect(url_for('project.list_projects'))
    document = services.get_document(current_user.id, project_id, document_id)
    if document is None:
        return redirect(url_for('annotate.annotate_next', project_id=project_id))
    options = json.dumps([{
        'value': label.value,
        'label': label.label,
        'color': label.color,
    } for label in project.labels])
    annotation_set = services.get_annotation_set(
        current_user.id, project_id, document_id)
    return render_template(
        'annotate.html',
        project=project,
        document=document,
        annotation_set=annotation_set,
        options=options,
    )


@view.route('/api/projects/<project_id>/documents/<document_id>/annotate')
@auth.login_required
def get_annotations(project_id, document_id):
    current_user = auth.current_user
    project = services.get_project(current_user.id, project_id)
    if project is None:
        return redirect(url_for('project.list_projects'))
    annotations = []
    annotation_set = services.get_annotation_set(
        current_user.id,
        project_id,
        document_id
    )
    if annotation_set is not None:
        for a in annotation_set.annotations:
            span = None
            if a.span is not None:
                span = {
                    'start': a.span.start,
                    'length': a.span.length
                }
            labels = []
            for l in a.labels:
                labels.append({
                    'value': l.value,
                    'label': l.label,
                    'order': l.order
                })
            annotations.append({
                'id': a.id,
                'span': span,
                'labels': labels,
            })
    return jsonify(jsend.success(annotations))


@view.route('/api/projects/<project_id>/documents/<document_id>/annotate', methods=['POST'])
@auth.login_required
def post_annotation(project_id, document_id):
    current_user = auth.current_user
    if 'data' in request.json and request.json['type'] == 'annotation':
        annotations = request.json['data']
        if isinstance(annotations, dict):
            annotations = [annotations]
        for annotation in annotations:
            annotation_id = None
            if 'id' in annotation:
                annotation_id = annotation.pop('id')
            # update annotation if exists
            if annotation_id is not None:
                status = services.update_annotation(
                    project_id,
                    current_user.id,
                    annotation_id,
                    annotation
                )
            else:
                status = False
            # if updating fails (or annotation is not present)
            #   add the annotation
            if not status:
                annotation_id = services.add_annotation(
                    project_id,
                    current_user.id,
                    document_id,
                    annotation
                )
            if annotation_id is None:
                return jsonify(jsend.fail({
                    'title': 'Invalid operation.',
                    'body': 'Invalid annotaiton.',
                }))
            return jsonify(jsend.success({
                'title': 'Update success.',
                'body': 'Successfully updated annotation.',
                'annotation_id': annotation_id,
            }))
    elif 'data' in request.json and request.json['type'] == 'flag':
        flag_status = bool(request.json['data']['status'])
        # update annotation set
        status = services.update_annotation_set(
            current_user.id,
            document_id,
            flagged=flag_status
        )
    elif 'data' in request.json:
        labels = request.json['data']['labels']
        for label in labels:
            label_value = label['value']
            label_status = label['status']
            if label_status:
                # add to labels
                annotations = services.filter_annotations_by_label(
                    current_user.id,
                    project_id,
                    document_id,
                    label_value
                )
                if len(annotations) == 0:
                    annotation_labels = {
                        'labels': [
                            {'value': label_value},
                        ],
                    }
                    status = services.add_annotation(
                        project_id,
                        current_user.id,
                        document_id,
                        annotation_labels
                    )
                else:
                    return jsonify(jsend.fail({
                        'title': 'Invalid operation.',
                        'body': 'Annotation already exists.'
                    }))
            else:
                # delete from labels
                annotations = services.filter_annotations_by_label(
                    current_user.id,
                    project_id,
                    document_id,
                    label_value
                )
                message_body = 'All annotations with label \'{}\' has been deleted.'
                label_label = None
                for annotation in annotations:
                    if label_label is None and len(annotation.labels) > 0:
                        label_label = annotation.labels[0].label
                    if annotation.span is None:
                        status = services.delete_annotation(
                            current_user.id,
                            project_id,
                            annotation.id
                        )
                    else:
                        message_body = 'Some annotations with label \'{}\' have not been deleted.'
                return jsonify(jsend.success({
                    'title': 'Update success.',
                    'body': message_body.format(label_label),
                }))
    elif request.json['type'] == 'skip':
        status = services.update_annotation_set(
            current_user.id, document_id, skipped=True)
    else:
        status = services.update_annotation_set(
            current_user.id, document_id, completed=True)
    return jsonify(jsend.success({
        'title': 'Update success.',
        'body': 'Successfully updated annotation.'
    }))


@view.route('/api/projects/<project_id>/documents/<document_id>/annotate', methods=['DELETE'])
@auth.login_required
def delete_annotation(project_id, document_id):
    current_user = auth.current_user
    annotation_id = request.json['data']['id']
    status = services.delete_annotation(
        current_user.id,
        project_id,
        annotation_id,
    )
    if not status:
        return jsonify(jsend.fail({
            'title': 'Delete failed.',
            'body': 'Could not delete annotation.',
        }))
    return jsonify(jsend.success({
        'title': 'Delete success.',
        'body': 'Successfully deleted annotation.',
    }))
