"""User router."""
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from textflow.api.dependencies import get_current_active_user, get_session
from textflow.database import op
from textflow import schemas

__all__ = [
    'router',
]

router = APIRouter(
    prefix='/users',
    tags=['Users'],
    responses={
        404: {'description': 'Not found'}
    },
)


@router.get('/me', response_model=schemas.User)
async def read_users_me(current_user: schemas.User =
                        Depends(get_current_active_user)):
    return current_user


@router.post('/', response_model=schemas.User)
async def create_user(
    user: schemas.User,
    session: Session = Depends(get_session),
):
    user = op.create_user(session, user=user)
    return user
