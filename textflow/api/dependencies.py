from datetime import timedelta, datetime
import typing
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError
import pydantic
from textflow.database import queries

from textflow.models import User

__all__ = [
    'oauth2_scheme',
]


ALGORITHM = 'HS256'
# openssl rand -hex 32
SECRET_KEY = '74c461c6be01eb70373a790ce7cf6c052c08772a63ea5ca087a7dad0e95c82a5'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/tokens/get/')


@pydantic.dataclasses.dataclass
class TokenData:
    username: typing.Union[str, None] = None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    users = queries.filter_users(username=token_data.username)
    print(users)
    user = users[0] if users else None
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


def create_access_token(
        data: dict,
        expires_delta: typing.Union[timedelta, None] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
