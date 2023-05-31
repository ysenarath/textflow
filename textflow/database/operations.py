import functools
import typing

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from textflow.database.pagination import Pagination, PaginationArgs, ModelType
from textflow import models, schemas
from textflow.models import (
    Assignment,
    User,
    Document,
    AnnotationSet,
    Project,
    Annotation,
    Label,
    Task,
)


ModelListType = typing.Union[Pagination[ModelType], typing.List[ModelType]]

PageType = typing.Optional[typing.Union[PaginationArgs, int]]


def from_orm(model):
    if isinstance(model, Pagination):
        model.items = list(map(from_orm, model.items))
        return model
    elif isinstance(model, list):
        return list(map(from_orm, model))
    output_type = type(model).__name__
    if not hasattr(models, output_type):
        return model
    Model = getattr(models, output_type)
    if not isinstance(model, Model):
        return model
    Schema = getattr(schemas, output_type)
    return Schema.from_orm(model)


def operation(func: typing.Callable):
    """Decorator for database operations.

    Parameters
    ----------
    func : typing.Callable
        Function.

    Returns
    -------
    typing.Callable
        Function.
    """
    @functools.wraps(func)
    def wrapper(session, **kwargs):
        for key, value in kwargs.items():
            schema_name = type(value).__name__
            if not hasattr(schemas, schema_name):
                continue
            Schema = getattr(schemas, schema_name)
            if not isinstance(value, Schema):
                continue
            Model = getattr(models, schema_name)
            cols = set(Model.__table__.columns.keys())
            kwargs[key] = Model(**value.dict(include=cols))
        output = func(session, **kwargs)
        return from_orm(output)
    return wrapper


@operation
def list_users(session: Session, *, page: PageType = None) \
        -> ModelListType[User]:
    """List all users.

    Parameters
    ----------
    session : Session
        Database session.
    page : PageType
        Page.

    Returns
    -------
    ModelListType[User]
        List of users.
    """
    return session.query(User).paginate(page)


@operation
def get_user(session: Session, *, user_id: int) -> typing.Optional[User]:
    """Get user by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    user_id : int
        User id.

    Returns
    -------
    typing.Optional[User]
        User.
    """
    return session.query(User).get(user_id)


@operation
def get_user_by(session: Session, *, username: str) -> \
        typing.Optional[User]:
    """Get user by username. Return None if not found.

    Parameters
    ----------
    username : str
        Username.

    Returns
    -------
    typing.Optional[User]
        User.
    """
    return session.query(User).filter_by(username=username).first()


@operation
def create_user(session: Session, *, user: User) -> User:
    """Add user.

    Parameters
    ----------
    session : Session
        Database session.
    user : User
        User.

    Returns
    -------
    User
        User.
    """
    try:
        session.add(user)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return user


@operation
def list_documents(
        session: Session,
        page: PageType = None,
) \
        -> ModelListType[Document]:
    """List all documents.

    Parameters
    ----------
    session : Session
        Database session.
    page : PageType
        Page.

    Returns
    -------
    ModelListType[Document]
        List of documents.
    """
    return session.query(User).paginate(page)


@operation
def list_documents_by(
        session: Session, *
        project_id: int,
        user_id: int = None,
        completed: bool = None,
        page: PageType = None,
) -> ModelListType[Document]:
    """List all documents.

    Parameters
    ----------
    session : Session
        Database session.
    project_id : int
        Project id.
    user_id : int
        User id.
    completed : bool
        Completed.
    page : PageType
        Page.

    Returns
    -------
    ModelListType[Document]
        List of documents.
    """
    query = session.query(Document)
    if project_id is not None:
        query = query \
            .filter(Document.project_id == project_id)
    if completed:
        # only documents that have annotation set can be marked completed
        query = query \
            .join(AnnotationSet, AnnotationSet.document_id == Document.id) \
            .filter(AnnotationSet.completed.is_(True))
    elif completed is not None:
        # make sure to keep all documents
        # both with and without annotation set can be marked not completed
        query = query \
            .leftjoin(
                AnnotationSet,
                AnnotationSet.document_id == Document.id
            ).filter(or_(
                AnnotationSet.completed.is_(False),
                AnnotationSet.completed.is_(None),
            ))
    if user_id is not None:
        query = query \
            .join(Project, Project.id == Document.project_id) \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    return query \
        .paginate(page)


@operation
def get_document(session: Session, *, document_id: int) -> \
        typing.Optional[Document]:
    """Get document by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    document_id : int
        Document id.

    Returns
    -------
    typing.Optional[Document]
        Document.
    """
    return session.query(Document) \
        .filter(Document.id == document_id) \
        .first()


@operation
def delete_documents_by(session: Session, *, project_id: int) -> \
        typing.Optional[Document]:
    """Delete document by id.

    Parameters
    ----------
    session : Session
        Database session.
    project_id : int
        Project id.

    Returns
    -------
    typing.Optional[Document]
        Document.
    """
    try:
        session.query(Document) \
            .filter(Document.project_id == project_id) \
            .delete()
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return None


@operation
def create_document(session: Session, *, doc: Document) -> Document:
    """Add document.

    Parameters
    ----------
    session : Session
        Database session.
    doc : Document
        Document.

    Returns
    -------
    Document
        Document.
    """
    try:
        session.add(doc)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return doc


@operation
def delete_document(session: Session, *, doc: Document) -> Document:
    """Delete document.

    Parameters
    ----------
    session : Session
        Database session.
    doc : Document
        Document.

    Returns
    -------
    Document
        Document.
    """
    try:
        session.delete(doc)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return doc


@operation
def delete_document_by(session: Session, *, document_id: int) -> Document:
    """Delete document by id.

    Parameters
    ----------
    session : Session
        Database session.
    id : int
        Document id.

    Returns
    -------
    Document
        Document.
    """
    doc = get_document(session, document_id)
    if doc is None:
        return None
    return delete_document(session, document_id)


@operation
def get_next_document(session: Session, *, user_id: int, project_id: int) \
        -> typing.Optional[Document]:
    """Get next document to annotate.

    Parameters
    ----------
    session : Session
        Database session.
    user_id : int
        User id.
    project_id : int
        Project id.

    Returns
    -------
    typing.Optional[Document]
        Document.
    """
    subquery = session.query(
        AnnotationSet.document_id,
        func.count(AnnotationSet.user_id).label('frequency')
    ) \
        .filter(AnnotationSet.completed.is_(True)) \
        .group_by(AnnotationSet.document_id) \
        .subquery()
    q = session.query(Document) \
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


@operation
def list_annotations_by_label(
        session: Session, *, user_id: int,
        document_id: int, label: Label,
        page: PageType = None
) \
        -> ModelListType[Annotation]:
    """List annotations by label.

    Parameters
    ----------
    session : Session
        Database session.
    user_id : int
        User id.
    document_id : int
        Document id.
    label : Label
        Label.
    page : PageType
        Page.

    Returns
    -------
    ModelListType[Annotation]
        List of annotations.
    """
    return session.query(Annotation) \
        .join(
            AnnotationSet,
            AnnotationSet.id == Annotation.annotation_set_id
    ) \
        .filter(
            AnnotationSet.user_id == user_id,
            AnnotationSet.document_id == document_id
    ) \
        .join(Document, Document.id == AnnotationSet.document_id) \
        .join(Annotation.labels) \
        .filter(Label.value == label.value) \
        .paginate(page)


@operation
def get_annotation_set(session: Session, *,
                       annotation_set_id: int) -> \
        typing.Optional[AnnotationSet]:
    """Get annotation set by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    id : int
        Annotation set id.

    Returns
    -------
    typing.Optional[AnnotationSet]
        Annotation set.
    """
    return session.query(AnnotationSet).get(annotation_set_id)


@operation
def create_annotation_set(session: Session, *,
                          annotation_set: AnnotationSet) -> \
        AnnotationSet:
    """Add annotation set.

    Parameters
    ----------
    session : Session
        Database session.
    annotation_set : AnnotationSet
        Annotation set.

    Returns
    -------
    AnnotationSet
        Annotation set.
    """
    try:
        session.add(annotation_set)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return annotation_set


@operation
def get_or_create_annotation_set_by_user_and_document(
    session: Session, *,
    user_id: int, document_id: int
) -> typing.Optional[AnnotationSet]:
    """Get or create annotation set by user and document.

    Parameters
    ----------
    session : Session
        Database session.
    user_id : int
        User id.
    document_id : int
        Document id.

    Returns
    -------
    AnnotationSet
        Annotation set.
    """
    annotation_set = session.query(AnnotationSet) \
        .filter_by(user_id=user_id, document_id=document_id) \
        .first()
    if annotation_set is None:
        annotation_set = AnnotationSet(
            user_id=user_id,
            document_id=document_id,
        )
        create_annotation_set(session, annotation_set)
    return annotation_set


# Alias
get_or_create_annotation_set = \
    get_or_create_annotation_set_by_user_and_document


@operation
def update_annotation_set(session: Session, *, annotation_set: AnnotationSet) \
        -> AnnotationSet:
    """Update annotation set.

    Parameters
    ----------
    session : Session
        Database session.
    annotation_set : AnnotationSet
        Annotation set.

    Returns
    -------
    AnnotationSet
        Annotation set.
    """
    try:
        session.merge(annotation_set)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return annotation_set


@operation
def get_label(session: Session, *,
              label_id: int) -> typing.Optional[Label]:
    """Get label by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    label_id : int
        Label id.

    Returns
    -------
    typing.Optional[Label]
        Label.
    """
    return session.query(Label).get(label_id)


@operation
def get_label_by(session: Session, *,
                 project_id: int, value: str) -> \
        typing.Optional[Label]:
    """Get label by project id and value. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    project_id : int
        Project id.
    value : str
        Label value.

    Returns
    -------
    typing.Optional[Label]
        Label.
    """
    return session.query(Label) \
        .filter_by(project_id=project_id, value=value) \
        .first()


@operation
def list_labels(session: Session, *,
                project_id: int, page: PageType = None) -> \
        ModelListType[Label]:
    """List labels.

    Parameters
    ----------
    session : Session
        Database session.
    project_id : int
        Project id.
    page : PageType
        Page.

    Returns
    -------
    ModelListType[Label]
        List of labels.
    """
    return session.query(Label) \
        .filter_by(project_id=project_id) \
        .paginate(page)


@operation
def delete_label(session: Session, *,
                 label: Label) -> Label:
    """Delete label.

    Parameters
    ----------
    session : Session
        Database session.
    label : Label
        Label.

    Returns
    -------
    Label
        Label.
    """
    try:
        session.delete(label)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return label


@operation
def create_annotation(session: Session, *,
                      annotation: Annotation) -> Annotation:
    """Add annotation.

    Parameters
    ----------
    session : Session
        Database session.
    annotation : Annotation
        Annotation.

    Returns
    -------
    Annotation
        Annotation.
    """
    try:
        session.add(annotation)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return annotation


@operation
def get_annotation(session: Session, *,
                   annotation_id: int) -> \
        typing.Optional[Annotation]:
    """Get annotation by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    annotation_id : int
        Annotation id.

    Returns
    -------
    typing.Optional[Annotation]
        Annotation.
    """
    return session.query(Annotation).get(annotation_id)


@operation
def update_annotation(session: Session, *,
                      annotation: Annotation) -> Annotation:
    """Update annotation.

    Parameters
    ----------
    session : Session
        Database session.
    annotation : Annotation
        Annotation.

    Returns
    -------
    Annotation
        Annotation.
    """
    try:
        session.merge(annotation)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return annotation


@operation
def delete_annotation(session: Session, *, annotation: Annotation) \
        -> Annotation:
    """Delete annotation.

    Parameters
    ----------
    session : Session
        Database session.
    annotation : Annotation
        Annotation.

    Returns
    -------
    Annotation
        Annotation.
    """
    try:
        session.delete(annotation)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return annotation


@operation
def get_project(session: Session, *,
                project_id: int) -> \
        typing.Optional[Project]:
    """Get project by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    project_id : int
        Project id.

    Returns
    -------
    typing.Optional[Project]
        Project.
    """
    return session.query(Project).get(project_id)


@operation
def list_projects_by(session: Session, *,
                     user_id: int = None,
                     page: PageType = None) -> \
        ModelListType[Project]:
    """List projects.

    Parameters
    ----------
    session : Session
        Database session.
    user_id : int
        User id.
    page : PageType
        Page.

    Returns
    -------
    ModelListType[Project]
        List of projects.
    """
    query = session.query(Project)
    if user_id is not None:
        query = query \
            .join(Assignment, Assignment.project_id == Project.id) \
            .filter(Assignment.user_id == user_id)
    return query.paginate(page)


@operation
def list_projects(session: Session) -> \
        ModelListType[Project]:
    """List projects.

    Parameters
    ----------
    session : Session
        Database session.

    Returns
    -------
    ModelListType[Project]
        List of projects.
    """
    return list_projects_by(session)


@operation
def create_project(session: Session, *, project: Project) -> Project:
    """Add project.

    Parameters
    ----------
    session : Session
        Database session.
    project : Project
        Project.

    Returns
    -------
    Project
        Project.
    """
    try:
        session.add(project)
        session.commit()
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return project


@operation
def update_project(session: Session, *, project: Project) -> Project:
    """Update project.

    Parameters
    ----------
    session : Session
        Database session.
    project : Project
        Project.

    Returns
    -------
    Project
        Project.
    """
    try:
        session.merge(project)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return project


@operation
def list_tasks_by(session: Session, *,
                  project_id: int = None,
                  user_id: int = None,
                  page: PageType = None) -> \
        ModelListType[Task]:
    """List tasks.

    Parameters
    ----------
    session : Session
        Database session.
    project_id : int
        Project id.
    user_id : int
        User id.
    page : PageType
        Page.

    Returns
    -------
    ModelListType[Task]
        List of tasks.
    """
    query = session.query(Task)
    if project_id is not None:
        query = query.filter_by(project_id=project_id)
    if user_id is not None:
        query = query \
            .join(Assignment, Assignment.project_id == Task.project_id) \
            .filter(Assignment.user_id == user_id)
    return query.paginate(page)


@operation
def get_task(session: Session, *, task_id: int) -> \
        typing.Optional[Task]:
    """Get task by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    task_id : int
        Task id.

    Returns
    -------
    typing.Optional[Task]
        Task.
    """
    return session.query(Task).get(task_id)


@operation
def get_assignment(session: Session, *, assignment_id: int) -> \
        typing.Optional[Assignment]:
    """Get assignment by id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    assignment_id : int
        Assignment id.

    Returns
    -------
    typing.Optional[Assignment]
        Assignment.
    """
    return session.query(Assignment).get(assignment_id)


@operation
def get_assignment_by(
    session: Session, *,
    project_id: int = None,
    user_id: typing.Optional[int] = None,
    username: typing.Optional[str] = None,
) -> typing.Optional[Assignment]:
    """Get assignment by user id and project id. Return None if not found.

    Parameters
    ----------
    session : Session
        Database session.
    user_id : typing.Optional[int]
        User id.
    username : typing.Optional[str]
        Username.
    project_id : typing.Optional[int]
        Project id.

    Returns
    -------
    typing.Optional[Assignment]
        Assignment.
    """
    query = session.query(Assignment) \
        .filter_by(project_id=project_id)
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    elif username is not None:
        query = query.join(User, User.id == Assignment.user_id)
        query = query.filter(User.username == username)
    else:
        raise ValueError('Either user_id or username must be provided.')
    return query.first()


@operation
def create_assignment(session: Session, *, assignment: Assignment):
    """Add assignment.

    Parameters
    ----------
    session : Session
        Database session.
    assignment : Assignment
        Assignment.

    Returns
    -------
    Assignment
        Assignment.
    """
    try:
        session.add(assignment)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return assignment


@operation
def update_assignment(session: Session, *, assignment: Assignment):
    """Update assignment.

    Parameters
    ----------
    session : Session
        Database session.
    assignment : Assignment
        Assignment.

    Returns
    -------
    Assignment
        Assignment.
    """
    try:
        session.merge(assignment)
    except Exception:
        session.rollback()
        raise
    else:
        session.commit()
    return assignment
