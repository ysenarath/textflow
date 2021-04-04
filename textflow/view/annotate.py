""" annotation view """
import json

from flask import redirect, url_for, render_template, request, jsonify, Blueprint, render_template_string, current_app

from textflow import services, auth
from textflow.utils import jsend

view = Blueprint('annotate_view', __name__)


@view.route('/projects/<project_id>/annotate')
@auth.login_required
def annotate_next(project_id):
    """Get next document for annotation and render that in view

    :return: rendered template
    """
    current_user = auth.current_user
    project = services.get_project(current_user.id, project_id)
    if project is None:
        return redirect(url_for('project_view.list_projects'))
    document = services.next_document(current_user.id, project_id)
    if document is None:
        return render_template('annotate.html', project=project)
    return redirect(url_for('annotate_view.annotate', project_id=project_id, document_id=document.id))


@view.route('/projects/<project_id>/annotate/<document_id>')
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
        return redirect(url_for('project_view.list_projects'))
    document = services.get_document(current_user.id, project_id, document_id)
    if document is None:
        return redirect(url_for('annotate_view.annotate_next', project_id=project_id))
    options = json.dumps([{'value': label.value, 'label': label.label} for label in project.labels])
    annotation_set = services.get_annotation_set(current_user.id, project_id, document_id)
    templates = current_app.config.get('templates', None)
    if templates is not None:
        project_template_path = 'projects/{}/annotate.html'.format(project_id)
        if project_template_path in templates:
            template = templates[project_template_path]
            return render_template_string(
                template, project=project, document=document,
                annotation_set=annotation_set, options=options
            )
    return render_template('annotate.html', project=project, document=document, annotation_set=annotation_set,
                           options=options)


@view.route('/api/projects/<project_id>/annotate/<document_id>')
@auth.login_required
def get_annotations(project_id, document_id):
    current_user = auth.current_user
    project = services.get_project(current_user.id, project_id)
    if project is None:
        return redirect(url_for('project_view.list_projects'))
    annotations = []
    annotation_set = services.get_annotation_set(current_user.id, project_id, document_id)
    if annotation_set is not None and project.type == 'sequence_labeling':
        for a in annotation_set.annotations:
            annotations.append(dict(id=a.id, label=a.label.value, span=dict(start=a.span.start, length=a.span.length)))
    elif annotation_set is not None:
        for a in annotation_set.annotations:
            annotations.append(dict(id=a.id, label=a.label.value))
    return jsonify(jsend.success(annotations))


@view.route('/api/projects/<project_id>/annotate/<document_id>', methods=['POST'])
@auth.login_required
def post_annotation(project_id, document_id):
    current_user = auth.current_user
    if 'data' in request.json and request.json['type'] == 'annotation':
        annotation = request.json['data']
        annotation_id, label_value = annotation['id'], annotation['label']
        annotation_span = dict(start=annotation['span']['start'], length=annotation['span']['length'])
        # update annotation if exists
        data = {'label': {'value': label_value}, 'span': annotation_span}
        status = services.update_annotation(project_id, current_user.id, annotation_id, data)
        # if updating fails add the annotation
        if not status:
            services.add_annotation(project_id, current_user.id, document_id, data)
    elif 'data' in request.json and request.json['type'] == 'flag':
        flag_status = bool(request.json['data']['status'])
        status = services.update_annotation_set(current_user.id, document_id, flagged=flag_status)
    elif 'data' in request.json:
        label_value = request.json['data']['value']
        label_status = request.json['data']['status']
        if label_status:
            # add to labels
            annotations = services. \
                filter_annotations_by_label(current_user.id, project_id, document_id, label_value)
            if len(annotations) == 0:
                annotation = dict(label=dict(value=label_value))
                status = services.add_annotation(project_id, current_user.id, document_id, annotation)
            else:
                return jsonify(jsend.fail({'title': 'Object not found.', 'body': 'Invalid operation request.'}))
        else:
            # delete from labels
            annotations = services \
                .filter_annotations_by_label(current_user.id, project_id, document_id, label_value)
            status = services.delete_annotation(current_user.id, project_id, annotations[0].id)
    elif request.json['type'] == 'skip':
        status = services.update_annotation_set(current_user.id, document_id, skipped=True)
    else:
        #  request.json['type'] == 'next':
        status = services.update_annotation_set(current_user.id, document_id, completed=True)
    return jsonify(jsend.success({'title': 'Update success.', 'body': 'Successfully updated annotation.'}))


@view.route('/api/projects/<project_id>/annotate/<document_id>', methods=['DELETE'])
@auth.login_required
def delete_annotation(project_id, document_id):
    current_user = auth.current_user
    annotation_id = request.json['data']['id']
    status = services.delete_annotation(current_user.id, project_id, annotation_id)
    if not status:
        return jsonify(jsend.fail({'title': 'Delete failed.', 'body': 'Annotation not found.'}))
    return jsonify(jsend.success({'title': 'Delete success.', 'body': 'Successfully deleted annotation.'}))
