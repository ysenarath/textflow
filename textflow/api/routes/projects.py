'''Project router.'''
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
    prefix='/projects',
    tags=['Projects'],
    dependencies=[Depends(get_current_active_user)],
    responses={
        404: {'description': 'Not found'}
    },
)


@router.get('/', response_model=typing.Union[
    Pagination[schemas.Project],
    typing.List[schemas.Project]
])
async def read_projects(
    q: dict[typing.Any] = Depends(get_listing_query_params),
    current_user: schemas.User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    # _: bool = Depends(roles_required()),
):
    projects = op.list_projects_by(
        session,
        user_id=None if current_user.role == UserRoleEnum.admin
        else current_user.id,
        **q,
    )
    return projects


@router.post('/')
async def create_project(
    project: schemas.ProjectBase,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required('admin')),
):
    project = schemas.Project(**project.dict())
    project = op.create_project(session, project=project)
    return project


@router.get('/{project_id}', response_model=schemas.Project)
async def read_project(
    project_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required('admin')),
):
    project = op.get_project(session, project_id=project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail='Project not found'
        )
    return project


@router.put('/{project_id}')
async def update_project(
    project_id: int,
    project: schemas.ProjectBase,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required('admin')),
):
    project = schemas.Project(id=project_id, **project.dict())
    project = op.update_project(session, project=project)
    return project
