"""User related schemas.

Classes
-------
User
Profile
Assignment

Enums
-----
UserRoleEnum
AssignmentRoleEnum
ThemeEnum
"""
import datetime
import enum
import typing
from werkzeug.security import generate_password_hash, check_password_hash

import pydantic

from textflow.schemas.base import Schema

__all__ = [
    'User',
    'Profile',
    'Assignment',
    'RefreshToken',
    'UserRoleEnum',
    'AssignmentRoleEnum',
    'ThemeEnum',
]


class UserRoleEnum(enum.Enum):
    admin = 'admin'
    default = 'default'


class AssignmentRoleEnum(enum.Enum):
    admin = 'admin'
    manager = 'manager'
    default = 'default'
    annotator = 'default'


class Assignment(Schema):
    user_id: int = pydantic.Field()
    project_id: int = pydantic.Field()
    role: AssignmentRoleEnum = pydantic.Field(default='default')


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


class RefreshToken(Schema):
    user_id: int = pydantic.Field()
    refresh_token: str = pydantic.Field()
    updated_on: typing.Optional[datetime.datetime] = \
        pydantic.Field(default=None)


class User(Schema):
    username: str = pydantic.Field()
    # non-nullable with default value
    role: UserRoleEnum = pydantic.Field(default='default')
    # plaintext password is not stored in database
    password: typing.Optional[pydantic.SecretStr] = \
        pydantic.Field(default=None)
    disabled: typing.Optional[bool] = pydantic.Field(default=False)
    # hashed password is stored in database
    hashed_password: typing.Optional[str] = pydantic.Field(default=None)
    id: typing.Optional[int] = pydantic.Field(default=None)

    def __init__(self, **kwargs):
        """Create a new user."""
        super(User, self).__init__(**kwargs)
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
