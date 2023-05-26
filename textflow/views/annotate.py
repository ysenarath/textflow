"""Annotate view module."""
from flask import redirect, url_for, request, jsonify, Blueprint

from textflow import auth
from textflow.views.base import render_template
from textflow.database import queries
from textflow.utils import jsend


__all__ = [
    'bp',
    'annotate_next',
]

bp = Blueprint('annotate', __name__)


@bp.route('/projects/<project_id>/annotate')
@auth.login_required
def annotate_next(project_id):
    """Get next document for annotation and redirect to annotation view.

    Returns
    -------
    redirect
        Redirect to annotation view.
    """
    project = queries.get_project(
        user_id=auth.current_user.id,
        project_id=int(project_id),
    )
    print(project)
    if project is None:
        return redirect(url_for('project.list_projects'))
    document = queries.next_document(
        user_id=auth.current_user.id,
        project_id=project_id,
    )
    if document is None:
        # render annotation interface without document information on
        # annotation
        return render_template(
            'annotate.html',
            project=project,
            document=None,
        )
    return redirect(url_for(
        'annotate.annotate',
        project_id=project.id,
        document_id=document.id,
    ))


@bp.route('/projects/<project_id>/documents/<document_id>/annotate')
@auth.login_required
def annotate(project_id, document_id):
    """Annotate document with provided ID.

    Parameters
    ----------
    project_id : int
        Project ID.
    document_id : int
        Document ID.

    Returns
    -------
    render_template : str
        Render annotation template.
    """
    document_id = int(document_id)
    project = queries.get_project(
        user_id=auth.current_user.id,
        project_id=project_id,
    )
    if project is None:
        print('project is none')
        return redirect(url_for('project.list_projects'))
    document = queries.get_document(
        # user_id, project_id, document_id
        user_id=auth.current_user.id,
        project_id=project_id,
        document_id=document_id,
    )
    if document is None:
        return redirect(url_for(
            'annotate.annotate_next',
            project_id=project_id
        ))
    return render_template(
        'annotate.html',
        project=project,
        document=document,
    )


@bp.route('/api/projects/<project_id>/documents/<document_id>')
@auth.login_required
def get_document(project_id, document_id):
    """Get document with provided ID.

    Parameters
    ----------
    project_id : int
        Project ID.
    document_id : int
        Document ID.

    Returns
    -------
    str
        JSON response.
    """
    document_id = int(document_id)
    document = queries.get_document(
        # user_id, project_id, document_id
        user_id=auth.current_user.id,
        project_id=project_id,
        document_id=document_id,
    )
    if document is None:
        return jsonify(jsend.fail({
            'document_id': f'Document with id {document_id} does not exist.'
        }))
    try:
        return jsonify(jsend.success(document.to_json()))
    except Exception:
        pass
    return jsonify(jsend.error(message='Unable to serialize the document.'))


@bp.route('/api/projects/<project_id>/documents/<document_id>/annotations')
@auth.login_required
def get_annotations(project_id, document_id):
    """Get annotations for document with provided ID.

    Parameters
    ----------
    project_id : int
        Project ID.
    document_id : int
        Document ID.

    Returns
    -------
    str
        JSON response.
    """
    document_id = int(document_id)
    annotation_set = queries.get_annotation_set(
        # user_id, project_id, document_id
        user_id=auth.current_user.id,
        project_id=project_id,
        document_id=document_id,
        # auth.current_user.id, project_id, document_id
    )
    if annotation_set is None:
        return jsonify(jsend.error(
            message='Unable to create or get the annotatons.'
        ))
    return jsonify(jsend.success(annotation_set.to_json()))


@bp.route(
    '/api/projects/<project_id>/documents/<document_id>/annotate',
    methods=['POST']
)
@auth.login_required
def post_annotation(project_id, document_id):
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
                status = queries.update_annotation(
                    # user_id, project_id, annotation_id, data
                    user_id=auth.current_user.id,
                    project_id=project_id,
                    annotation_id=annotation_id,
                    data=annotation,
                )
            else:
                status = False
            # if updating fails (or annotation is not present)
            #   add the annotation
            if not status:
                annotation_id = queries.add_annotation(
                    # user_id, project_id, document_id, data
                    user_id=auth.current_user.id,
                    project_id=project_id,
                    document_id=document_id,
                    data=annotation,
                )
            if annotation_id is None:
                resp = jsend.error(message='Unable to add annotation.')
                return jsonify(resp)
            return jsonify(jsend.success({
                'title': 'Update success.',
                'body': 'Successfully updated annotation.',
                'annotation_id': annotation_id,
            }))
    elif 'data' in request.json and request.json['type'] == 'flag':
        flag_status = bool(request.json['data']['status'])
        # update annotation set
        status = queries.update_annotation_set(
            # user_id, document_id, **params
            user_id=auth.current_user.id,
            document_id=document_id,
            flagged=flag_status,
            # current_user.id,
            # document_id,
            # flagged=flag_status
        )
    elif 'data' in request.json:
        labels = request.json['data']['labels']
        for label in labels:
            label_value = label['value']
            label_status = label['status']
            # all annotaitons updated successfully
            message_body = 'Annotations have been updated successfully.'
            if label_status:
                # add to labels
                annotations = queries.filter_annotations_by_label(
                    # user_id, project_id, document_id, label_value
                    user_id=auth.current_user.id,
                    project_id=project_id,
                    document_id=document_id,
                    label_value=label_value,
                )
                # annotation does not exist
                if len(annotations) > 0:
                    continue
                annotation_labels = {
                    'labels': [
                        {'value': label_value},
                    ],
                }
                status = queries.add_annotation(
                    # user_id, project_id, document_id, data
                    user_id=auth.current_user.id,
                    project_id=project_id,
                    document_id=document_id,
                    data=annotation_labels,
                )
            else:
                # delete from labels
                annotations = queries.filter_annotations_by_label(
                    # user_id, project_id, document_id, label_value
                    user_id=auth.current_user.id,
                    project_id=project_id,
                    document_id=document_id,
                    label_value=label_value,
                )
                message_body = 'All annotations with label \
                    \'{}\' has been deleted.'
                label_label = None
                for annotation in annotations:
                    if label_label is None and len(annotation.labels) > 0:
                        label_label = annotation.labels[0].label
                    if annotation.span is None:
                        status = queries.delete_annotation(
                            # user_id, project_id, annotation_id
                            user_id=auth.current_user.id,
                            project_id=project_id,
                            annotation_id=annotation.id,
                        )
                    else:
                        message_body = 'Some annotations with label \'{}\' \
                            have not been deleted.'
                message_body = message_body.format(label_label)
        return jsonify(jsend.success({
            'title': 'Update success.',
            'body': message_body,
        }))
    elif request.json['type'] == 'skip':
        status = queries.update_annotation_set(
            # user_id, document_id, **params
            user_id=auth.current_user.id,
            document_id=document_id,
            skipped=True,
        )
    else:
        status = queries.update_annotation_set(
            # user_id, document_id, **params
            user_id=auth.current_user.id,
            document_id=document_id,
            completed=True,
        )
    return jsonify(jsend.success({
        'title': 'Update success.',
        'body': 'Successfully updated annotation.'
    }))


@bp.route(
    '/api/projects/<project_id>/documents/<document_id>/annotate',
    methods=['DELETE']
)
@auth.login_required
def delete_annotation(project_id, document_id):
    annotation_id = request.json['data']['id']
    if queries.delete_annotation(
        # user_id, project_id, annotation_id
        user_id=auth.current_user.id,
        project_id=project_id,
        annotation_id=annotation_id,
    ):
        return jsonify(jsend.success({
            'title': 'Delete success.',
            'body': 'Successfully deleted annotation.',
        }))
    return jsonify(jsend.fail({
        'title': 'Delete failed.',
        'body': 'Could not delete annotation.',
    }))
