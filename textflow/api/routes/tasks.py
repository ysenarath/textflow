"""Task routes."""
import typing
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from textflow.api.dependencies import (
    get_current_active_user,
    get_listing_query_params,
    roles_required,
    get_session,
)

from textflow import schemas
from textflow.database import op, Pagination
from textflow.schemas.user import UserRoleEnum

__all__ = [
    'router',
]

router = APIRouter(
    prefix='/projects/{project_id}/tasks',
    tags=['Tasks'],
    dependencies=[Depends(get_current_active_user)],
    responses={
        404: {'description': 'Not found'}
    },
)


@router.get('/', response_model=typing.Union[
    Pagination[schemas.Task],
    typing.List[schemas.Task]
])
@router.get('', response_model=typing.Union[
    Pagination[schemas.Task],
    typing.List[schemas.Task]
])
async def read_tasks(
    project_id: int,
    q: dict[typing.Any] = Depends(get_listing_query_params),
    current_user: schemas.User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required('default')),
):
    tasks = op.list_tasks_by(
        session,
        project_id=project_id,
        user_id=None if current_user.role == UserRoleEnum.admin
        else current_user.id,
        **q,
    )
    return tasks


@router.post('/', response_model=schemas.Task, status_code=201)
@router.post('', response_model=schemas.Task, status_code=201)
async def create_task(
    project_id: int,
    task: schemas.TaskBase,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required('admin')),
):
    task = schemas.Task(project_id=project_id, **task.dict())
    task = op.create_task(session, task=task)
    return task


@router.get('/{task_id}', response_model=schemas.Task)
async def read_task(
    project_id: int,
    task_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required('default')),
):
    task = op.get_task(session, project_id=project_id, task_id=task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail='Project not found'
        )
    return task


@router.put('/{task_id}')
async def update_task(
    project_id: int,
    task_id: int,
    task: schemas.TaskBase,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required('admin')),
):
    task = schemas.Task(id=task_id, project_id=project_id, **task.dict())
    task = op.update_task(session, task=task)
    return task
