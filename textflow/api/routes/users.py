"""User router."""
from fastapi import APIRouter, Depends

from textflow.api.dependencies import get_current_active_user
from textflow.models import User


__all__ = [
    'router',
]

router = APIRouter()


@router.get('/users/me/')
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
