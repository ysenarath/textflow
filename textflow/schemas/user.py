"""User related schemas.

Classes
-------
User
Profile
Assignment
"""
import enum
import typing
from werkzeug.security import generate_password_hash, check_password_hash

import pydantic

from textflow.schemas.base import Schema

__all__ = [
    'User',
    'Profile',
    'Assignment',
    'RoleEnum',
    'ThemeEnum',
]


class RoleEnum(enum.Enum):
    admin = 'admin'
    manager = 'manager'
    annotator = 'annotator'
    default = 'default'


class Assignment(Schema):
    user_id: int = pydantic.Field()
    project_id: int = pydantic.Field()
    role: RoleEnum = pydantic.Field(default='default')


class ThemeEnum(enum.Enum):
    light = 'light'
    dark = 'dark'
    auto = 'auto'


class Profile(Schema):
    user_id: int = pydantic.Field()
    first_name: typing.Optional[str] = \
        pydantic.Field(default=None)
    last_name: typing.Optional[str] = \
        pydantic.Field(default=None)
    email: typing.Optional[str] = pydantic.Field(
        default=None,
    )
    theme: typing.Optional[ThemeEnum] = pydantic.Field(
        default='light',
    )


class User(Schema):
    username: str = pydantic.Field()
    # plaintext password is not stored in database
    password: typing.Optional[pydantic.SecretStr] = \
        pydantic.Field(default=None)
    disabled: typing.Optional[bool] = pydantic.Field(default=False)
    # hashed password is stored in database
    hashed_password: typing.Optional[str] = pydantic.Field(default=None)
    id: typing.Optional[int] = pydantic.Field(default=None)

    def __init__(self, *args, **kwargs):
        """Create a new user."""
        super(User, self).__init__(*args, **kwargs)
        if self.password is not None:
            self.set_password(self.password)

    @pydantic.validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v

    def set_password(self, password):
        """Set the password.

        Parameters
        ----------
        password : str
            Password of user.

        Returns
        -------
        User
            User with password set.
        """
        if isinstance(password, pydantic.SecretStr):
            password = password.get_secret_value()
        self.hashed_password = generate_password_hash(password)
        return self

    def verify_password(self, password):
        """Verify the password.

        Parameters
        ----------
        password : str
            Password of user.

        Returns
        -------
        bool
            True if password is correct, False otherwise.
        """
        return check_password_hash(self.hashed_password, password)
