from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from textflow.api.dependencies import (
    oauth2_scheme,
    create_access_token,
    get_session,
)
from textflow.database import op

__all__ = [
    'router',
]

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix='/tokens',
    tags=['Tokens'],
)


@router.get('/')
async def read_tokens(token: str = Depends(oauth2_scheme)):
    return {'token': token}


@router.post('/get/')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    # get user from database
    user = op.get_user_by(session, username=form_data.username)
    if not user:
        raise HTTPException(
            status_code=400,
            detail='Incorrect username or password'
        )
    if not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=400,
            detail='Incorrect username or password'
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}
