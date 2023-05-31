from datetime import timedelta, datetime
import typing
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from jose import jwt, JWTError
import pydantic

from textflow.database import db, op
from textflow import schemas

__all__ = [
    'oauth2_scheme',
]


ALGORITHM = 'HS256'
# openssl rand -hex 32
SECRET_KEY = '74c461c6be01eb70373a790ce7cf6c052c08772a63ea5ca087a7dad0e95c82a5'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/tokens/get/')


def get_session():
    with db.session() as sess:
        yield sess


@pydantic.dataclasses.dataclass
class TokenData:
    username: typing.Union[str, None] = None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> schemas.User:
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
    user = op.get_user_by(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user)
) -> schemas.User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


def create_access_token(
        data: dict,
        expires_delta: typing.Union[timedelta, None] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def roles_required(
    role: typing.Union[str, typing.Set[str]],
    raise_exception: bool = True
) -> typing.Callable:
    if not isinstance(role, set):
        if isinstance(role, str):
            role = [role]
        role = set(role)

    def check_user_role(
        project_id: typing.Optional[int] = None,
        user: schemas.User = Depends(get_current_active_user),
        session: Session = Depends(get_session),
    ) -> bool:
        if not role:
            return
        if project_id is None and role:
            assignment = None
        else:
            assignment = op.get_assignment_by(
                session,
                user_id=user.id,
                project_id=project_id
            )
        if not assignment or assignment.role not in role:
            if not raise_exception:
                return False
            raise HTTPException(
                status_code=403,
                detail='You do not have permission to perform this action',
            )
        return True
    return check_user_role
