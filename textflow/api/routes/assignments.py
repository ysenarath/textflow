"""Routes for assignments."""
import typing
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from textflow.api.dependencies import (
    get_current_active_user,
    roles_required,
    get_session,
)

from textflow import schemas
from textflow.database import op

__all__ = [
    'router',
]


router = APIRouter(
    prefix='/projects/{project_id}/users',
    tags=['Assignments'],
    dependencies=[Depends(get_current_active_user)],
    responses={
        404: {'description': 'Not found'}
    },
)


@router.post(
    '/{username}/role',
    response_model=schemas.Assignment,
)
async def assign_project(
    project_id: int,
    username: str,
    role: schemas.RoleEnum,
    # the user must be admin to update the role of a user
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required({'admin'})),
):
    """Assign a user to a project.

    Notes
    -----
    The user doing this action must be admin of the project to assign
    a user to the project.

    Parameters
    ----------
    project_id : int
        ID of project.
    username : str
        Username of user.
    role : RoleEnum
        Role of user.

    Returns
    -------
    Assignment
        Assignment of user to project.
    """
    user = op.get_user_by(session, username=username)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    assignment = schemas.Assignment(
        user_id=user.id,
        project_id=project_id,
        role=role.role
    )
    assignment = op.create_assignment(
        session, assignment=assignment
    )
    return assignment


@router.put(
    '/{username}/role',
    response_model=schemas.Assignment,
    responses={
        404: {'description': 'Assignment not found'},
    }
)
async def update_project_role(
    project_id: int,
    username: str,
    role: schemas.RoleEnum,
    session: Session = Depends(get_session),
    # the user must be admin to update the role of a user
    _: bool = Depends(roles_required({'admin'})),
):
    """Update the role of a user in a project.

    Notes
    -----
    The user doing this action must be admin of the project to update 
    the role of a user.

    Parameters
    ----------
    project_id : int
        ID of project.
    username : str
        Username of user.
    role : RoleEnum
        Role of user.

    Returns
    -------
    Assignment
        Assignment of user to project.
    """
    user = op.get_user_by(session, username=username)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    assignment = op.get_assignment_by(
        session,
        user_id=user.id,
        project_id=project_id
    )
    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail='Assignment not found'
        )
    assignment.role = role.role
    assignment = op.update_assignment(
        session,
        assignment=assignment,
    )
    return assignment


@router.get(
    '/',
    response_model=typing.List[schemas.User],
    responses={
        404: {'description': 'Project not found'},
    }
)
def read_assignments_of_project(
    project_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required({'admin'})),
) -> typing.List[schemas.User]:
    project = op.get_project(session, project_id=project_id)
    return [assignment for assignment in project.assignments]
