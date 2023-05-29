"""User model.

This module contains the User model.

Classes
-------
User
Profile
Assignment
"""
import dataclasses
import enum
import typing
from flask import g
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import pydantic

from textflow.database import db

__all__ = [
    'User',
    'Profile',
    'Assignment',
]


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class Assignment(db.ModelMixin):
    """Assignment of user to project.

    Attributes
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    role : str
        Role of user in project.
    """
    __table__ = db.Table(
        'assignment',
        db.mapper_registry.metadata,
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                  primary_key=True),
        db.Column('project_id', db.Integer, db.ForeignKey('project.id'),
                  primary_key=True),
        db.Column('role', db.String(512), nullable=False, default='default'),
    )

    user_id: int = pydantic.Field()
    project_id: int = pydantic.Field()
    role: str = pydantic.Field(default='default')


class ThemeEnum(enum.Enum):
    light = 'light'
    dark = 'dark'
    auto = 'auto'


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class Profile(db.ModelMixin):
    """Profile of user.

    Attributes
    ----------
    user_id : int
        User id.
    first_name : str
        First name of user.
    last_name : str
        Last name of user.
    email : str
        Email of user.
    theme : str
        Theme of user.
    """
    __table__ = db.Table(
        'profile',
        db.mapper_registry.metadata,
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                  primary_key=True),
        db.Column('first_name', db.String(512), nullable=True),
        db.Column('last_name', db.String(512), nullable=True),
        db.Column('email', db.String(120), unique=True, nullable=True),
        db.Column('theme', db.String(80), nullable=False, default='light'),
    )

    __mapper_args__ = {
        'properties': dict(
            user=db.relationship('User', back_populates='profile')
        )
    }

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


@db.mapper_registry.mapped
@pydantic.dataclasses.dataclass
class User(db.ModelMixin, UserMixin):
    """User model.

    Attributes
    ----------
    id : int
        Primary key.
    username : str
        Username of user.
    password : str
        Password of user.
    projects : list of Assignment
        Projects of user.
    profile : Profile
        Profile of user.
    jobs : list of BackgroundJob
        Background jobs related to this user.
    """
    __table__ = db.Table(
        'user',
        db.mapper_registry.metadata,
        db.Column('id', db.Integer, primary_key=True, autoincrement=True),
        db.Column('disabled', db.Boolean, default=False),
        db.Column('username', db.String(80), unique=True, nullable=False),
        db.Column('password', db.String(512), nullable=False,
                  key='hashed_password'),
    )

    __mapper_args__ = {
        'properties': dict(
            profile=db.relationship(
                'Profile', uselist=False, back_populates='user',
                lazy='joined', cascade='all, delete-orphan'
            ),
            jobs=db.relationship(
                'BackgroundJob',
                backref='user', lazy='joined'
            ),
            projects=db.relationship(
                'Assignment',
                backref='user', lazy=True,
                cascade='all, delete-orphan',
            )
        )
    }

    username: str = pydantic.Field()
    # plaintext password is not stored in database
    password: typing.Optional[pydantic.SecretStr] = \
        pydantic.Field(default=None)
    disabled: bool = pydantic.Field(default=False)
    # hashed password is stored in database
    hashed_password: typing.Optional[str] = \
        pydantic.Field(default=None, alias='hashed_password')
    id: typing.Optional[int] = \
        pydantic.Field(None)

    def __post_init_post_parse__(self):
        """Create a new user."""
        if self.password is not None:
            self.set_password(self.password)
        if self.profile is None and self.id is not None:
            # create a new profile for the user
            self.profile = Profile(user_id=self.id)

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

    def __repr__(self):
        """Get the representation of the user.

        Returns
        -------
        str
            Representation of the user.
        """
        return '<User {}>'.format(self.username)

    @property
    def role(self):
        """Get the role of the user.

        Returns
        -------
        str
            Role of the user.
        """
        if 'current_user_role' in g:
            return g.current_user_role
        return None
