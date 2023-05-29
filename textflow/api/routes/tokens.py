from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm


from textflow.api.dependencies import oauth2_scheme, create_access_token
from textflow.database import queries

__all__ = [
    'router',
]

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


@router.get('/tokens/')
async def read_tokens(token: str = Depends(oauth2_scheme)):
    return {'token': token}


@router.post('/tokens/get/')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # get user from database
    users = queries.filter_users(username=form_data.username)
    user = users[0] if users else None
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
