import math

from sqlalchemy import or_, func, and_
from sqlalchemy.exc import SQLAlchemyError

from textflow.models import (
    User,
    Document,
    AnnotationSet,
    Annotation,
    AnnotationSpan,
    Label,
    Task,
    Project,
    Assignment,
    BackgroundJob,
)
from textflow.database.base import database as db

__all__ = [
    'ignore',
    'list_users',
    'get_user',
    'filter_users',
    'list_documents_completed_by_user',
    'next_document',
    'filter_annotations_by_label',
    'get_annotation_set',
    'get_label',
    'filter_label',
    'list_labels',
    'delete_label',
    'add_annotation',
    'get_annotation',
    'update_annotation',
    'delete_annotation',
    'get_project',
    'list_projects',
    'list_tasks',
    'get_task',
    'update_annotation_set',
    'get_document',
    'delete_documents',
    'filter_document',
    'list_assignments',
    'get_assignment',
    'remove_assignment',
    'generate_project_report',
    'list_background_jobs',
    'get_background_job',
]

# `ignore` is used to indicate that the object is not used in the query
# this is different from using None because None is used to indicate that
# the object attribute is not set (or None)
ignore = object()


def list_users():
    """List all users.

    Returns
    -------
    list
        List of users.
    """
    return User.query.all()


def get_user(*, user_id):
    """Get user by id.

    Parameters
    ----------
    user_id : int
        User id.

    Returns
    -------
    User
        User object.
    """
    return User.query.get(int(user_id))


def filter_users(**kwargs):
    """Filter users.

    Parameters
    ----------
    **kwargs
        Filter arguments.

    Returns
    -------
    list
        List of users.
    """
    filters = {}
    if 'username' in kwargs:
        filters['username'] = kwargs['username']
    return User.query.filter_by(**filters).all()


def list_documents_completed_by_user(*, user_id, project_id, flagged=False,
                                     paginate=None, paginate_kwargs=None):
    """List all documents in a project annotated by provided user.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    flagged : bool, optional
        Filter by flagged status.
    paginate : bool, optional
        Paginate results.
    paginate_kwargs : dict, optional
        Pagination arguments.
    """
    q = db.session.query(Document, AnnotationSet) \
        .join(AnnotationSet, AnnotationSet.document_id == Document.id) \
        .filter(
            Document.project_id == project_id,
            AnnotationSet.user_id == user_id,
            AnnotationSet.completed.is_(True),
    ) \
        .order_by(AnnotationSet.updated_on.desc()) \
        .distinct()
    if flagged is not None:
        q = q.filter(AnnotationSet.flagged.is_(flagged))
    if paginate:
        if hasattr(paginate, 'to_dict'):
            paginate_kwargs = paginate.to_dict()
        return q.paginate(**paginate_kwargs)
    return q.all()


def next_document(*, user_id, project_id):
    """Get next document to annotate.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.

    Returns
    -------
    Document
        Document object.
    """
    # get documents that were only annotated by less than
    #  -  required redundancy (project.redundancy) amount
    # Number of time each document is annotated
    subquery = db.session.query(
        AnnotationSet.document_id,
        func.count(AnnotationSet.user_id).label('frequency')
    ) \
        .filter(AnnotationSet.completed.is_(True)) \
        .group_by(AnnotationSet.document_id) \
        .subquery()
    q = Document.query \
        .join(Project, Project.id == Document.project_id) \
        .join(Assignment, Assignment.project_id == Project.id) \
        .outerjoin(subquery, Document.id == subquery.c.document_id) \
        .outerjoin(AnnotationSet, and_(
            AnnotationSet.document_id == Document.id,
            AnnotationSet.user_id == Assignment.user_id
        )) \
        .filter(Document.project_id == project_id) \
        .filter(Assignment.user_id == user_id) \
        .filter(or_(
            subquery.c.frequency.is_(None),
            Project.redundancy > subquery.c.frequency
        )) \
        .filter(or_(
            AnnotationSet.completed.is_(None),
            AnnotationSet.completed.is_(False)
        )) \
        .filter(or_(
            AnnotationSet.skipped.is_(None),
            AnnotationSet.skipped.is_(False)
        ))
    return q.first()


def filter_annotations_by_label(*, user_id, project_id, document_id,
                                label_value):
    """Filter annotations by label.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    document_id : int
        Document id.
    label_value : str
        Value of label.

    Returns
    -------
    list
        List of annotations.
    """
    return Annotation.query \
        .join(
            AnnotationSet,
            AnnotationSet.id == Annotation.annotation_set_id
        ) \
        .filter(
            AnnotationSet.user_id == user_id,
            AnnotationSet.document_id == document_id
        ) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(Document.project_id == project_id) \
        .join(Annotation.labels) \
        .filter(Label.value == label_value) \
        .all()


def get_annotation_set(*, user_id, project_id, document_id):
    """Get annotation set.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    document_id : int
        Document id.

    Returns
    -------
    AnnotationSet
        AnnotationSet object.
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
        .filter(
            Document.project_id == project_id,
            AnnotationSet.document_id == document_id,
            AnnotationSet.user_id == user_id
        ) \
        .first()
    if annotation_set is None:
        # create annotation set if not exist
        annotation_set = AnnotationSet(
            document_id=document_id,
            user_id=user_id
        )
        try:
            db.session.add(annotation_set)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return None
    return annotation_set


def get_label(*, label_id):
    """Get label by id.

    Parameters
    ----------
    label_id : int
        Label id.

    Returns
    -------
    Label
        Label object.
    """
    return Label.query.get(int(label_id))


def filter_label(*, project_id, value):
    """Filter label of project by value.

    Parameters
    ----------
    project_id : int
        Project id.
    value : str
        Label value.

    Returns
    -------
    Label
        Label object.
    """
    return Label.query \
        .join(Task, Task.id == Label.task_id) \
        .filter(Task.project_id == project_id) \
        .filter(Label.value == value) \
        .first()


def list_labels(*, project_id):
    """List all labels of project.

    Parameters
    ----------
    project_id : int
        Project id.

    Returns
    -------
    list
        List of labels.
    """
    return Label.query.join(Task, Task.id == Label.task_id) \
        .filter(Task.project_id == project_id) \
        .order_by(Label.order) \
        .all()


def delete_label(*, label_id):
    """Delete label by id.

    Parameters
    ----------
    label_id : int
        Label id.

    Returns
    -------
    bool
        True if label is deleted, False otherwise.
    """
    obj = get_label(label_id=label_id)
    if obj is None:
        return False
    try:
        db.session.delete(obj)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return False
    return True


def add_annotation(*, user_id, project_id, document_id, data):
    """Add annotation.

    Parameters
    ----------
    project_id : int
        Project id.
    user_id : int
        User id.
    document_id : int
        Document id.
    data : dict
        Annotation data.

    Returns
    -------
    int
        Annotation id.
    """
    # annotation set is supposed to be not None (create if not exist)
    annotation_set = get_annotation_set(
        user_id=user_id,
        project_id=project_id,
        document_id=document_id,
    )
    annotation = Annotation(
        annotation_set_id=annotation_set.id
    )
    if 'span' in data:
        # set a span if exists in data
        annotation.span = AnnotationSpan(
            start=data['span']['start'],
            length=data['span']['length']
        )
    for label in data['labels']:
        # get the (actual) label from the value of the label
        label = filter_label(
            project_id=project_id,
            value=label['value'],
        )
        # add labels to annotation
        annotation.labels.append(label)
    try:
        annotation_set.annotations.append(annotation)
        db.session.commit()
        return annotation.id
    except SQLAlchemyError:
        db.session.rollback()
        return None


def get_annotation(*, user_id, project_id, annotation_id):
    """Get annotation by id.

    Parameters
    ----------
    project_id : int
        Project id.
    user_id : int
        User id.
    annotation_id : int
        Annotation id.

    Returns
    -------
    Annotation or None
        Annotation object.
    """
    return Annotation.query \
        .join(
            AnnotationSet,
            Annotation.annotation_set_id == AnnotationSet.id
        ) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(
            AnnotationSet.user_id == user_id,
            Document.project_id == project_id
        ) \
        .filter(Annotation.id == annotation_id) \
        .first()


def update_annotation(*, user_id, project_id, annotation_id, data):
    """Update annotation.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    annotation_id : int
        Annotation id to update.
    data : dict
        Annotation data.
    """
    annotation = get_annotation(
        user_id=user_id,
        project_id=project_id,
        annotation_id=annotation_id
    )
    if annotation is None:
        return False
    # delete all associated labels of annotation
    annotation.labels.clear()
    # add new labels
    successfull = True
    for label in data['labels']:
        # get the (actual) label from the value of the label
        label = filter_label(
            project_id=project_id,
            value=label['value']
        )
        # if label is not found, rollback and return False
        if label is None:
            successfull = False
            break
        annotation.labels.append(label)
    if not successfull:
        db.session.rollback()
        return False
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return False
    return True


def delete_annotation(*, user_id, project_id, annotation_id):
    """Delete annotation.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    annotation_id : int
        Annotation id.

    Returns
    -------
    bool
        True if annotation is deleted, False otherwise.
    """
    # delete annotation by id but make sure the provided params are correct
    annotation = Annotation.query \
        .filter(Annotation.id == annotation_id) \
        .join(
            AnnotationSet,
            Annotation.annotation_set_id == AnnotationSet.id
        ) \
        .filter(AnnotationSet.user_id == user_id) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .filter(Document.project_id == project_id) \
        .first()
    if annotation is None:
        return False
    try:
        db.session.delete(annotation)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return False
    return True


def get_project(*, user_id, project_id):
    """Get project by id.

    Notes
    -----
    If user_id is `ignore`, then the project is returned without checking
    whether the user is assigned to the project.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.

    Returns
    -------
    Project
        Project object.
    """
    q = Project.query.filter(Project.id == project_id)
    if user_id is ignore:
        return q.first()
    return q.join(Assignment, Assignment.project_id == Project.id) \
        .filter(Assignment.user_id == user_id) \
        .first()


def list_projects(*, user_id, paginate=None, paginate_kwargs=None):
    """List all projects assigned to the user.

    Notes
    -----
    If user_id is `ignore`, then all projects are returned.

    Parameters
    ----------
    user_id : int
        User id.
    paginate : bool, optional
        Paginate results.
    paginate_kwargs : dict, optional
        Pagination arguments.

    Returns
    -------
    list
        List of projects.
    """
    q = Project.query
    if user_id is not ignore:
        q = q.join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    if paginate:
        if hasattr(paginate, 'to_dict'):
            paginate_kwargs = paginate.to_dict()
        return q.paginate(**paginate_kwargs)
    return q.all()


def list_tasks(*, user_id, project_id):
    """List all tasks of project.

    Notes
    -----
    If user_id is `ignore`, then all tasks are returned.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.

    Returns
    -------
    list
        List of tasks.
    """
    project_id = int(project_id)
    if user_id is ignore:
        return Project.query.get(project_id).tasks
    return Project.query \
        .join(Assignment, Assignment.project_id == Project.id) \
        .filter(Assignment.user_id == user_id, Project.id == project_id) \
        .first().tasks


def get_task(*, user_id, task_id):
    """Get task by id.

    Notes
    -----
    If user_id is `ignore`, then the task is returned without checking

    Parameters
    ----------
    user_id : int
        User id.
    task_id : int
        Task id.

    Returns
    -------
    Task
        Task object.
    """
    task_id = int(task_id)
    q = Task.query.filter(Task.id == task_id)
    if user_id is not ignore:
        q = q.join(Project, Project.id == Task.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    return q.first()


def update_annotation_set(*, user_id, document_id, **params):
    """Update annotation set.

    Parameters
    ----------
    user_id : int
        User id.
    document_id : int
        Document id.
    **params
        Annotation set parameters.

    Returns
    -------
    bool
        True if annotation set is updated, False otherwise.
    """
    annotation_set = AnnotationSet.query \
        .filter(
            AnnotationSet.user_id == user_id,
            AnnotationSet.document_id == document_id
        ).first()
    if annotation_set is None:
        return False
    if 'completed' in params:
        annotation_set.completed = params['completed']
    if 'skipped' in params:
        annotation_set.skipped = params['skipped']
    if 'flagged' in params:
        annotation_set.flagged = params['flagged']
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return False
    return True


def get_document(*, user_id, project_id, document_id):
    """Get document by id.

    Notes
    -----
    If user_id is `ignore`, then the document is returned without checking
    whether the user is assigned to the project.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    document_id : int
        Document id.

    Returns
    -------
    Document
        Document object.
    """
    q = Document.query \
        .filter(Document.id == document_id)
    if user_id is not ignore:
        q = q.filter(Document.project_id == project_id) \
            .join(Project, Project.id == Document.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    return q.first()


def delete_documents(*, user_id, project_id):
    """Delete all documents of project.

    Notes
    -----
    If user_id is `ignore`, then all documents of the project are deleted.

    Examples
    --------
    >>> for num_docs_deleted, num_docs_total in delete_documents(...):
    ...     print(f'{num_docs_deleted} / {num_docs_total} documents deleted')
    >>> # or if you need only the final result
    >>> num_docs_deleted, num_docs_total = yield from delete_documents(...)

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.

    Yields
    ------
    tuple
        Number of documents deleted and total number of documents.

    Returns
    -------
    tuple
        Number of documents deleted and total number of documents.
    """
    q = Document.query.filter(Document.project_id == project_id)
    if user_id is not ignore:
        # delete the projects that are assigned to a given user
        q = q.join(Project, Project.id == Document.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    num_docs_total = q.count()
    num_docs_deleted = 0
    while True:
        documents = q.limit(1000).all()
        num_docs_found = len(documents)
        if num_docs_found == 0:
            # finished deleting all documents
            break
        for d in documents:
            db.session.delete(d)
            num_docs_found += 1
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            # encountered an error while deleting documents
            # stop deleting documents
            break
        num_docs_deleted += num_docs_found
        yield num_docs_deleted, num_docs_total
    return num_docs_deleted, num_docs_total


def filter_document(*, user_id, project_id, id_str):
    q = Document.query \
        .filter(Document.project_id == project_id, Document.id_str == id_str)
    if user_id is ignore:
        return q.first()
    return q.join(Project, Project.id == Document.project_id) \
        .join(Assignment, Assignment.project_id == Project.id) \
        .filter(Assignment.user_id == user_id) \
        .first()


def list_assignments(*, project_id):
    """List all assignments of project.

    Parameters
    ----------
    project_id : int
        Project id.

    Returns
    -------
    list
        List of assignments.
    """
    return Assignment.query.filter(Assignment.project_id == project_id).all()


def get_assignment(*, user_id, project_id):
    """Get assignment by user id and project id.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.

    Returns
    -------
    Assignment
        Assignment object.
    """
    return Assignment.query.filter(
        Assignment.user_id == user_id,
        Assignment.project_id == project_id,
    ).first()


def remove_assignment(*, user_id, project_id):
    """Remove assignment by user id and project id.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.

    Returns
    -------
    bool
        True if assignment is removed, False otherwise.
    """
    a = get_assignment(user_id=user_id, project_id=project_id)
    if a is None:
        return False
    try:
        db.session.delete(a)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return False
    return True


def generate_project_report(*, user_id, project_id):
    """Generate status report.

    Notes
    -----
    If user_id is `ignore`, then the status report is generated for the
    project.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int, optional
        Project id.

    Returns
    -------
    dict
        Project status report.
    """
    if user_id is ignore:
        subquery = db.session.query(AnnotationSet.document_id, func.count(
            AnnotationSet.user_id,
        ).label('frequency')) \
            .filter(AnnotationSet.completed.is_(True)) \
            .group_by(AnnotationSet.document_id) \
            .subquery()
        num_completed = Document.query \
            .join(Project, Project.id == Document.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .outerjoin(subquery, Document.id == subquery.c.document_id) \
            .outerjoin(AnnotationSet, and_(
                AnnotationSet.document_id == Document.id,
                AnnotationSet.user_id == Assignment.user_id,
            )) \
            .filter(Document.project_id == project_id) \
            .filter(AnnotationSet.completed.is_(True)) \
            .filter(AnnotationSet.skipped.is_(False)) \
            .filter(Project.redundancy <= subquery.c.frequency) \
            .distinct(Document.id) \
            .count()
        # number of documents in project
        num_documents = Document.query \
            .filter(Document.project_id == project_id) \
            .distinct(Document.id) \
            .count()
        if num_documents == 0:
            progress = 0
        else:
            progress = math.floor(num_completed * 100 / num_documents)
        return {
            'num_documents': num_documents,
            'num_completed': num_completed,
            'num_remaining': num_documents - num_completed,
            'progress': progress,
        }
    else:
        num_completed = Document.query \
            .join(AnnotationSet, AnnotationSet.document_id == Document.id) \
            .join(Project, Project.id == Document.project_id) \
            .filter(
                AnnotationSet.user_id == user_id,
                Document.project_id == project_id,
                AnnotationSet.completed.is_(True)
            ) \
            .count()
        # number of assigned documents
        num_documents = Document.query \
            .filter(Document.project_id == project_id) \
            .outerjoin(AnnotationSet, and_(
                AnnotationSet.document_id == Document.id,
                AnnotationSet.user_id == user_id,
            )) \
            .filter(or_(
                AnnotationSet.skipped.is_(None),
                AnnotationSet.skipped.is_(False),
            )) \
            .count()
        if num_documents == 0:
            progress = 100
        else:
            progress = math.floor(num_completed * 100 / num_documents)
        return {
            'num_documents': num_documents,
            'num_completed': num_completed,
            'num_remaining': num_documents - num_completed,
            'progress': progress,
        }


def list_background_jobs(*, user_id, project_id):
    """List all background jobs.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.

    Returns
    -------
    list
        List of background jobs.
    """
    q = BackgroundJob.query
    if user_id is not ignore:
        q = q.filter(BackgroundJob.user_id == user_id)
    if project_id is not ignore and project_id is not None:
        q = q.filter(BackgroundJob.project_id == project_id)
    return q.all()


def get_background_job(*, user_id, project_id, job_id):
    """Get background job.

    Parameters
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    job_id : str
        Job id.

    Returns
    -------
    BackgroundJob
        BackgroundJob object.
    """
    q = BackgroundJob.query
    if user_id is not ignore:
        q = q.filter(BackgroundJob.user_id == user_id)
    if project_id is not ignore:
        q = q.filter(BackgroundJob.project_id == project_id)
    # Return an instance based on the given primary key identifier,
    # or None if not found.
    return q.get(job_id)
