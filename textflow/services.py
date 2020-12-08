""" Includes all service calls to database. """
from sqlalchemy import or_, func, and_
from sqlalchemy.exc import SQLAlchemyError

from textflow.db import db
from textflow.model.annotation import AnnotationSet, Annotation, AnnotationSpan
from textflow.model.document import Document
from textflow.model.label import Label
from textflow.model.project import Project
from textflow.model.user import User, Assignment


def get_user(user_id):
    """ Loads user from ID

    :param user_id: gets user from ID
    :return: user if exist
    """
    return User.query.get(int(user_id))


def filter_users(**kwargs):
    """ Filter username

    :param kwargs: {username}
    :return: Returns one user with provided details
    """
    filters = {}
    if 'username' in kwargs:
        filters['username'] = kwargs['username']
    return User.query.filter_by(**filters).all()


def list_documents(project_id, user_id, paginate=None, paginate_kwargs=None):
    """ Gets documents completed by provided user.

    :param project_id: project id
    :param user_id: id of user for getting completed documents
    :param paginate: whether to paginate output
    :param paginate_kwargs: paginate keyword args
    :return: completed documents
    """
    q = Document.query \
        .filter(Document.project_id == project_id) \
        .join(AnnotationSet, AnnotationSet.document_id == Document.id) \
        .filter(AnnotationSet.user_id == user_id, AnnotationSet.completed.is_(True)) \
        .order_by(AnnotationSet.updated_on.desc())
    if paginate is not None:
        return q.paginate(**paginate_kwargs)
    return q.all()


def next_document(user_id, project_id):
    """ Returns next document for annotation by provided user.

    :param user_id: user id
    :param project_id: project id
    :param project_id: project id
    :return: document if exist else none
    """
    # get documents that were only annotated by less than
    #  -  required redundancy (project.redundancy) amount
    # Number of time each document is annotated
    subquery = db.session.query(AnnotationSet.document_id, func.count(AnnotationSet.user_id).label('frequency')) \
        .group_by(AnnotationSet.document_id) \
        .subquery()
    return Document.query \
        .filter(Document.project_id == project_id) \
        .join(Project, Project.id == Document.project_id) \
        .join(Assignment, Assignment.project_id == Project.id) \
        .outerjoin(subquery, Document.id == subquery.c.document_id) \
        .filter(or_(subquery.c.frequency.is_(None),
                    Project.redundancy > subquery.c.frequency)) \
        .outerjoin(AnnotationSet,
                   and_(AnnotationSet.document_id == Document.id, AnnotationSet.user_id == Assignment.user_id)) \
        .filter(or_(AnnotationSet.completed.is_(False),
                    AnnotationSet.user_id != user_id,
                    AnnotationSet.completed.is_(None))) \
        .first()


def get_annotation(project_id, user_id, annotation_id):
    """ Gets annotation by id

    :return:
    """
    return Annotation.query \
        .join(AnnotationSet, Annotation.annotation_set_id == AnnotationSet.id) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(AnnotationSet.user_id == user_id, Document.project_id == project_id) \
        .filter(Annotation.id == annotation_id) \
        .first()


def filter_annotations_by_label(user_id, project_id, document_id, label_value):
    """ Gets annotations by label of document

    :return:
    """
    return Annotation.query \
        .join(AnnotationSet, AnnotationSet.id == Annotation.annotation_set_id) \
        .filter(AnnotationSet.user_id == user_id, AnnotationSet.document_id == document_id) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(Document.project_id == project_id) \
        .join(Label, Annotation.label_id == Label.id) \
        .filter(Label.value == label_value) \
        .all()


def add_annotation(project_id, user_id, document_id, data):
    """ Add annotation to set of annotations

    :param project_id: project id
    :param user_id: user id
    :param document_id: document id
    :param data: annotation params
    :return: adds annotation and return status
    """
    label = filter_label(project_id, value=data['label']['value'])
    annotation_set = get_annotation_set(user_id, project_id, document_id)
    if 'span' in data:
        annotation_span = AnnotationSpan(start=data['span']['start'], length=data['span']['length'])
        annotation = Annotation(label_id=label.id, span=annotation_span, annotation_set_id=annotation_set.id)
    else:
        annotation = Annotation(label_id=label.id, annotation_set_id=annotation_set.id)
    try:
        annotation_set.annotations.append(annotation)
        db.session.commit()
        return True
    except SQLAlchemyError as err:
        db.session.rollback()
        return False


def delete_annotation(user_id, project_id, annotation_id):
    """ Delete annotation by id

    :return: whether annotation is deleted or not
    """
    annotation = Annotation.query \
        .filter(Annotation.id == annotation_id) \
        .join(AnnotationSet, Annotation.annotation_set_id == AnnotationSet.id) \
        .filter(AnnotationSet.user_id == user_id) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(Document.project_id == project_id) \
        .first()
    if annotation is not None:
        db.session.delete(annotation)
        db.session.commit()
    else:
        return False
    return True


def get_annotation_set(user_id, project_id, document_id):
    """ Returns annotation set

    :param user_id: user id
    :param project_id: project id
    :param document_id: document id
    :return: annotation set for user document pair
    """
    # check whether user can edit document annotations
    d = Document.query \
        .filter(Document.id == document_id) \
        .join(Project, Project.id == Document.project_id) \
        .filter(Project.id == project_id) \
        .join(Assignment, Assignment.project_id == Project.id) \
        .filter(Assignment.user_id == user_id) \
        .first()
    if d is None:
        return None
    # try getting annotation set
    annotation_set = AnnotationSet.query \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(Document.project_id == project_id, AnnotationSet.document_id == document_id,
                AnnotationSet.user_id == user_id) \
        .first()
    if annotation_set is None:
        # create annotation set if not exist
        annotation_set = AnnotationSet(document_id=document_id, user_id=user_id)
        db.session.add(annotation_set)
        db.session.commit()
    return annotation_set


def filter_label(project_id, value):
    """ Gets label from value [unique for project]

    :param project_id: project id
    :param value: value
    :return: label
    """
    return Label.query.filter_by(project_id=project_id, value=value).one()


def update_annotation(project_id, user_id, annotation_id, data):
    """ Update annotation [only label]

    :param project_id: project id
    :param user_id: user id
    :param annotation_id: annotation id
    :param data: parameters for updating annotations
    :return: whether updated or not
    """
    annotation = get_annotation(project_id, user_id, annotation_id)
    if annotation is None:
        return False
    else:
        label = filter_label(project_id, data['label']['value'])
        annotation.label = label
        db.session.commit()
    return True


def get_project(user_id, project_id):
    """ Gets project provided ID only if it is assigned to user

    :param user_id: user id
    :param project_id: project id
    :return: get project
    """
    return Project.query \
        .join(Assignment, Assignment.project_id == Project.id) \
        .filter(Assignment.user_id == user_id, Project.id == project_id) \
        .first()


def list_projects(user_id):
    """ Gets user provided ID

    :param user_id: user id
    :return: get user
    """
    return Project.query \
        .join(Assignment, Assignment.project_id == Project.id) \
        .filter(Assignment.user_id == user_id) \
        .all()


def update_annotation_set(user_id, document_id, **params):
    """ Update annotated set

    :param user_id:
    :param document_id:
    :return:
    """
    annotation_set = AnnotationSet.query \
        .filter(AnnotationSet.user_id == user_id, AnnotationSet.document_id == document_id) \
        .first()
    if annotation_set is None:
        return False
    if 'completed' in params:
        annotation_set.completed = params['completed']
    db.session.commit()
    return True


def get_document(user_id, project_id, document_id):
    """ get document from document ID

    :param user_id: user id
    :param project_id: project id
    :param document_id: document id
    :return:
    """
    return Document.query \
        .filter(Document.id == document_id, Document.project_id == project_id) \
        .join(Project, Project.id == Document.project_id) \
        .join(Assignment, Assignment.project_id == Project.id) \
        .filter(Assignment.user_id == user_id) \
        .first()