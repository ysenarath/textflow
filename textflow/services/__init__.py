"""Includes all service calls to database. """

from sqlalchemy import or_, func, and_, distinct
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm

from textflow.model import *
from textflow.services.base import service, database as db


@service
def list_users(ctx):
    """Loads user from ID

    :param ctx: context
    :return: user if exist
    """
    return User.query.all()


@service
def get_user(ctx, user_id):
    """Loads user from ID

    :param ctx: context
    :param user_id: gets user from ID
    :return: user if exist
    """
    return User.query.get(int(user_id))


@service
def filter_users(ctx, **kwargs):
    """Filter username

    :param ctx: context
    :param kwargs: {username}
    :return: Returns all user with provided details
    """
    filters = {}
    if 'username' in kwargs:
        filters['username'] = kwargs['username']
    return User.query.filter_by(**filters).all()


@service
def list_documents(ctx, project_id, user_id, flagged=False, paginate=None, paginate_kwargs=None):
    """Gets documents completed by provided user.

    :param ctx: context
    :param project_id: project id
    :param user_id: id of user for getting completed documents
    :param flagged: whether to filter in only flagged items
    :param paginate: whether to paginate output
    :param paginate_kwargs: paginate keyword args
    :return: completed documents
    """
    q = db.session.query(Document, AnnotationSet) \
        .join(AnnotationSet, AnnotationSet.document_id == Document.id) \
        .filter(Document.project_id == project_id, AnnotationSet.user_id == user_id,
                AnnotationSet.completed.is_(True)) \
        .order_by(AnnotationSet.updated_on.desc()) \
        .distinct()
    if flagged is not None:
        q = q.filter(AnnotationSet.flagged.is_(flagged))
    if paginate is not None:
        return q.paginate(**paginate_kwargs)
    return q.all()


@service
def next_document(ctx, user_id, project_id):
    """Returns next document for annotation by provided user.

    :param ctx: context
    :param user_id: user id (not username)
    :param project_id: project id
    :return: document if exist else none
    """
    # get documents that were only annotated by less than
    #  -  required redundancy (project.redundancy) amount
    # Number of time each document is annotated
    subquery = db.session.query(AnnotationSet.document_id, func.count(AnnotationSet.user_id).label('frequency')) \
        .filter(AnnotationSet.completed.is_(True)) \
        .group_by(AnnotationSet.document_id) \
        .subquery()
    q = Document.query \
        .join(Project, Project.id == Document.project_id) \
        .join(Assignment, Assignment.project_id == Project.id) \
        .outerjoin(subquery, Document.id == subquery.c.document_id) \
        .outerjoin(AnnotationSet,
                   and_(AnnotationSet.document_id == Document.id, AnnotationSet.user_id == Assignment.user_id)) \
        .filter(Document.project_id == project_id) \
        .filter(Assignment.user_id == user_id) \
        .filter(or_(subquery.c.frequency.is_(None), Project.redundancy > subquery.c.frequency)) \
        .filter(or_(AnnotationSet.completed.is_(None), AnnotationSet.completed.is_(False))) \
        .filter(or_(AnnotationSet.skipped.is_(None), AnnotationSet.skipped.is_(False)))
    return q.first()


@service
def get_annotation(ctx, project_id, user_id, annotation_id):
    """Gets annotation by id

    :param ctx: context
    :param project_id: project id
    :param user_id: user id (not username)
    :param annotation_id: annotation id
    :return: annotation with annotation id
    """
    return Annotation.query \
        .join(AnnotationSet, Annotation.annotation_set_id == AnnotationSet.id) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(AnnotationSet.user_id == user_id, Document.project_id == project_id) \
        .filter(Annotation.id == annotation_id) \
        .first()


@service
def filter_annotations_by_label(ctx, user_id, project_id, document_id, label_value):
    """Gets annotations by label of document for the user.

    :return: all annotations with provided label value
    """
    return Annotation.query \
        .join(AnnotationSet, AnnotationSet.id == Annotation.annotation_set_id) \
        .filter(AnnotationSet.user_id == user_id, AnnotationSet.document_id == document_id) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(Document.project_id == project_id) \
        .join(Annotation.labels) \
        .filter(Label.value == label_value) \
        .all()


@service
def add_annotation(ctx, project_id, user_id, document_id, data):
    """Add annotation to set of annotations

    :param ctx: context
    :param project_id: project id
    :param user_id: user id (not username)
    :param document_id: document id
    :param data: annotation params, label details
    :return: adds annotation and return status
    """
    annotation_set = get_annotation_set(user_id, project_id, document_id)
    if 'span' in data:
        annotation_span = AnnotationSpan(
            start=data['span']['start'],
            length=data['span']['length']
        )
        annotation = Annotation(
            span=annotation_span,
            annotation_set_id=annotation_set.id
        )
    else:
        annotation = Annotation(
            annotation_set_id=annotation_set.id
        )
    for label in data['labels']:
        # get the (actual) label from the value of the label
        label = filter_label(project_id, value=label['value'])
        annotation.labels.append(label)
    try:
        annotation_set.annotations.append(annotation)
        db.session.commit()
        return annotation.id
    except SQLAlchemyError as err:
        db.session.rollback()
        return None


@service
def delete_annotation(ctx, user_id, project_id, annotation_id):
    """Delete annotation by id

    :return: whether annotation is deleted or not
    """
    # delete annotation by id but make sure the provided params are correct
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


@service
def get_annotation_set(ctx, user_id, project_id, document_id):
    """Returns annotation set

    :param ctx: context
    :param user_id: user id (not username)
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
        annotation_set = AnnotationSet(
            document_id=document_id, user_id=user_id)
        db.session.add(annotation_set)
        db.session.commit()
    return annotation_set


@service
def get_label(ctx, label_id):
    """Loads user from ID

    :param ctx: context
    :param label_id: label id
    :return: user if exist
    """
    return Label.query.get(int(label_id))


@service
def filter_label(ctx, project_id, value):
    """Gets label from value [unique for project]

    :param ctx: context
    :param project_id: project id
    :param value: value
    :return: label
    """
    return Label.query.filter_by(project_id=project_id, value=value).first()


@service
def list_labels(ctx, project_id, user_id):
    """List all labels

    :param ctx: context
    :param project_id: project id
    :return: label
    """
    return Label.query.filter_by(project_id=project_id).order_by(Label.order).all()


@service
def delete_label(ctx, label_id):
    """Delete label

    :param ctx:
    :param label_id:
    :return:
    """
    obj = get_label(label_id)
    if obj is None:
        return False
    db.session.delete(obj)
    db.session.commit()
    return True


@service
def update_annotation(ctx, project_id, user_id, annotation_id, data):
    """Update annotation [only label]

    :param ctx: context
    :param project_id: project id
    :param user_id: user id (not username)
    :param annotation_id: annotation id
    :param data: parameters for updating annotations
    :return: whether updated or not
    """
    annotation = get_annotation(project_id, user_id, annotation_id)
    status = True
    if annotation is None:
        status = False
    else:
        # delete all associated labels of annotation
        annotation.labels.clear()
        # add new labels
        for label in data['labels']:
            # get the (actual) label from the value of the label
            label = filter_label(project_id, value=label['value'])
            if label is not None:
                annotation.labels.append(label)
            else:
                status = False
                break
    if status:
        db.session.commit()
    else:
        db.session.rollback()
    return status


@service
def get_project(ctx, user_id, project_id):
    """Gets project provided ID only if it is assigned to user

    :param ctx: context
    :param user_id: user id (not username)
    :param project_id: project id
    :return: get project
    """
    if ctx.ignore_user:
        return Project.query \
            .filter(Project.id == project_id) \
            .first()
    else:
        return Project.query \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id, Project.id == project_id) \
            .first()


@service
def list_projects(ctx, user_id, paginate=None, paginate_kwargs=None):
    """Gets user provided ID

    :param ctx: context
    :param user_id: user id (not username)
    :param paginate: whether to paginate output
    :param paginate_kwargs: paginate keyword args
    :return: get user
    """
    if ctx.ignore_user:
        q = Project.query
    else:
        q = Project.query \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    if paginate is not None:
        return q.paginate(**paginate_kwargs)
    return q.all()


@service
def update_annotation_set(ctx, user_id, document_id, **params):
    """Update annotated set

    :param ctx: context
    :param user_id: user id (not username)
    :param document_id: document id
    :return: update status
    """
    annotation_set = AnnotationSet.query \
        .filter(AnnotationSet.user_id == user_id, AnnotationSet.document_id == document_id) \
        .first()
    if annotation_set is None:
        return False
    if 'completed' in params:
        annotation_set.completed = params['completed']
    if 'skipped' in params:
        annotation_set.skipped = params['skipped']
    if 'flagged' in params:
        annotation_set.flagged = params['flagged']
    db.session.commit()
    return True


@service
def get_document(ctx, user_id, project_id, document_id):
    """Get document from document ID

    Admin level access will ignore user_id, project_id parameters.

    :param ctx: context
    :param user_id: user id (not username)
    :param project_id: project id
    :param document_id: document id
    :return:
    """
    if ctx.ignore_user:
        query = Document.query \
            .filter(Document.id == document_id)
    else:
        query = Document.query \
            .filter(Document.id == document_id, Document.project_id == project_id) \
            .join(Project, Project.id == Document.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    return query.first()


@service
def delete_documents(ctx, user_id, project_id):
    """Get document from document ID

    Admin level access will ignore user_id, project_id parameters.

    :param ctx: context
    :param user_id: user id (not username)
    :param project_id: project id
    :return:
    """
    num_rows_deleted = 0
    if ctx.ignore_user:
        query = Document.query.filter(Document.project_id == project_id)
    else:
        # delete the projects that are assigned to a given user
        query = Document.query \
            .filter(Document.project_id == project_id) \
            .join(Project, Project.id == Document.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    with tqdm(desc='Deleting documents', total=query.count()) as t:
        while True:
            documents = query.limit(1000).all()
            delta_t = len(documents)
            if delta_t == 0:
                break
            try:
                for d in documents:
                    db.session.delete(d)
                db.session.commit()
                num_rows_deleted += delta_t
                if t.total - t.n - delta_t >= 0:
                    t.update(delta_t)
                elif t.total - t.n >= 0:
                    t.update(t.total - t.n)
            except SQLAlchemyError as e:
                db.session.rollback()
    return num_rows_deleted


@service
def filter_document(ctx, user_id, project_id, id_str):
    """Gets and returns the first document by project id and id str

    Admin level access will ignore user_id parameter.

    :param ctx: context
    :param user_id: user id (not username)
    :param project_id: project id
    :param id_str:
    :return:
    """
    if ctx.ignore_user:
        return Document.query \
            .filter(Document.project_id == project_id, Document.id_str == id_str) \
            .first()
    else:
        return Document.query \
            .filter(Document.project_id == project_id, Document.id_str == id_str) \
            .join(Project, Project.id == Document.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id) \
            .first()


@service
def list_assignments(ctx, project_id):
    """Gets assignment using provided user and project id.

    :param ctx: context
    :param project_id: project id
    :return: Assigment if exist else None
    """
    return Assignment.query.filter(Assignment.project_id == project_id).all()


@service
def get_assignment(ctx, user_id, project_id):
    """Gets assignment using provided user and project id.

    :param ctx: context
    :param user_id: user id
    :param project_id: project id
    :return: Assigment if exist else None
    """
    return Assignment.query.filter(Assignment.user_id == user_id, Assignment.project_id == project_id).first()


@service
def remove_assignment(ctx, user_id, project_id):
    """Remove assignment of a user from the provided project.

    :param ctx: context
    :param user_id: user id
    :param project_id: project id
    :return: status
    """
    a = get_assignment(user_id=user_id, project_id=project_id)
    if a is not None:
        db.session.delete(a)
        db.session.commit()
    else:
        return False
    return True


@service
def list_plugin_names(ctx, project_id, plugin_type):
    if plugin_type == 'dataset':
        p = get_project.ignore_user(user_id=None, project_id=project_id)
        project_spec_datasets = datasets.list_names(project_id)
        project_type_datasets = datasets.list_names(p.type)
        return list(set(project_spec_datasets + project_type_datasets))
    elif plugin_type == 'estimator':
        p = get_project.ignore_user(user_id=None, project_id=project_id)
        project_spec_estimators = estimators.list_names(project_id)
        project_type_estimators = estimators.list_names(p.type)
        return list(set(project_spec_estimators + project_type_estimators))
    else:
        return None


@service
def get_dataset(ctx, project_id, name=None):
    """Gets dataset from project ID.

    :param ctx: context
    :param project_id: project id
    :param name: dataset name (gets `default` if None)
    :return: dataset
    """
    plugin = datasets.get_plugin(project_id, name)
    if plugin is None:
        p = get_project.ignore_user(user_id=None, project_id=project_id)
        plugin = datasets.get_plugin(p.type, name)
    # get annotation set to build the model
    annotation_sets = AnnotationSet.query \
        .outerjoin(Document, Document.id == AnnotationSet.document_id) \
        .filter(Document.project_id == project_id, AnnotationSet.completed.is_(True)).all()
    return plugin(annotation_sets)


@service
def get_estimator(ctx, project_id, name=None):
    """Gets (non trained) model from project ID.

    :param ctx: context
    :param project_id: project id
    :param name: model name (gets `default` if None)
    :return: model
    """
    plugin = estimators.get_plugin(project_id, name)
    if plugin is None:
        p = get_project.ignore_user(user_id=None, project_id=project_id)
        plugin = estimators.get_plugin(p.type, name)
    return plugin()


@service
def generate_status_report(ctx, user_id, project_id=None):
    """Generates and returns status report

    :param ctx: context
    :param user_id: user id (not username)
    :param project_id: project id
    :return: status report
    """
    if project_id is not None:
        num_completed = Document.query \
            .join(AnnotationSet, AnnotationSet.document_id == Document.id) \
            .join(Project, Project.id == Document.project_id) \
            .filter(AnnotationSet.user_id == user_id, Document.project_id == project_id,
                    AnnotationSet.completed.is_(True)) \
            .count()
        # num_annotations = db.session.query(Label.value, Label.label, func.count(distinct(Annotation.id))) \
        #     .outerjoin(Annotation, Annotation.label_id == Label.id) \
        #     .filter(Label.project_id == project_id) \
        #     .outerjoin(AnnotationSet, AnnotationSet.id == Annotation.annotation_set_id) \
        #     .filter(or_(AnnotationSet.user_id == user_id, AnnotationSet.user_id.is_(None))) \
        #     .group_by(Label.label) \
        #     .order_by(Label.order) \
        #     .all()
        num_assigned = Document.query \
            .filter(Document.project_id == project_id) \
            .outerjoin(AnnotationSet, and_(AnnotationSet.document_id == Document.id,
                                           AnnotationSet.user_id == user_id)) \
            .filter(or_(AnnotationSet.skipped.is_(None), AnnotationSet.skipped.is_(False))) \
            .count()
        if num_assigned == 0:
            progress = 100
        else:
            progress = num_completed * 100 / num_assigned
        return dict(
            # num_annotations={v: (l, c) for v, l, c in num_annotations},
            num_assigned=num_assigned,
            num_completed=num_completed,
            progress=progress,
        )
    return {}


@service
def get_project_status(ctx, project_id):
    subquery = db.session.query(AnnotationSet.document_id, func.count(AnnotationSet.user_id)
                                .label('frequency')) \
        .filter(AnnotationSet.completed.is_(True)) \
        .group_by(AnnotationSet.document_id) \
        .subquery()
    num_completed = Document.query \
        .join(Project, Project.id == Document.project_id) \
        .join(Assignment, Assignment.project_id == Project.id) \
        .outerjoin(subquery, Document.id == subquery.c.document_id) \
        .outerjoin(AnnotationSet,
                   and_(AnnotationSet.document_id == Document.id, AnnotationSet.user_id == Assignment.user_id)) \
        .filter(Document.project_id == project_id) \
        .filter(AnnotationSet.completed.is_(True)) \
        .filter(AnnotationSet.skipped.is_(False)) \
        .filter(Project.redundancy <= subquery.c.frequency) \
        .distinct(Document.id) \
        .count()
    num_documents = Document.query \
        .filter(Document.project_id == project_id) \
        .distinct(Document.id) \
        .count()
    return {
        'num_completed': num_completed,
        'num_documents': num_documents,
        'num_remaining': num_documents - num_completed,
        'percentage': int(num_completed / num_documents) * 100 if num_documents > 0 else 0,
    }


@service
def list_tasks(ctx, user_id=None, project_id=None):
    """Lists tasks.

    :param ctx: context
    :param user_id: user id
    :param project_id: project id
    :return: list of tasks
    """
    q = Task.query
    if user_id is not None:
        return q.filter(Task.user_id == user_id).all()
    if project_id is not None:
        q = q.filter(Task.project_id == project_id)
    return q.all()


@service
def get_task(ctx, user_id=None, project_id=None, task_id=None):
    """Gets task.

    :param ctx: context
    :param task_id: task id
    :return: task
    """
    q = Task.query
    if user_id is not None:
        return q.filter(Task.user_id == user_id)
    if project_id is not None:
        q = q.filter(Task.project_id == project_id)
    # Return an instance based on the given primary key identifier,
    # or None if not found.
    return q.get(task_id)
