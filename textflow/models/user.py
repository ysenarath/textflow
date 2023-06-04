"""User model.

This module contains the User model.

Classes
-------
User
Profile
Assignment
"""
from flask_login import UserMixin

import sqlalchemy as sa
from textflow import schemas

from textflow.models.base import mapper_registry, ModelMixin

__all__ = [
    'User',
    'Assignment',
    'Profile',
    'RefreshToken',
]


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class Assignment(ModelMixin):
    """User assignment of user to project.

    Attributes
    ----------
    user_id : int
        User id.
    project_id : int
        Project id.
    role : str
        Role of user in project.
    """
    __table__ = sa.Table(
        'assignment',
        mapper_registry.metadata,
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'),
                  primary_key=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('project.id'),
                  primary_key=True),
        sa.Column('role', sa.Enum(schemas.AssignmentRoleEnum),
                  nullable=False, default=schemas.AssignmentRoleEnum.default),
    )


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class Profile(ModelMixin):
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
    __table__ = sa.Table(
        'profile',
        mapper_registry.metadata,
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'),
                  primary_key=True),
        sa.Column('first_name', sa.String(512), nullable=True),
        sa.Column('last_name', sa.String(512), nullable=True),
        sa.Column('email', sa.String(120), unique=True, nullable=True),
        sa.Column('theme', sa.Enum(schemas.ThemeEnum),
                  nullable=False, default=schemas.ThemeEnum.light),
    )

    __mapper_args__ = {
        'properties': dict(
            user=sa.orm.relationship('User', back_populates='profile')
        )
    }


@mapper_registry.mapped
class RefreshToken(ModelMixin):
    __tablename__ = "refresh_token"

    __table__ = sa.Table(
        'refresh_token',
        mapper_registry.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey(
            'user.id', ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column('refresh_token', sa.String(512), nullable=False),
        sa.Column(
            'created_on', sa.DateTime, server_default=sa.func.now()
        ),
    )

    __mapper_args__ = {
        'properties': dict(
            user=sa.orm.relationship('User', back_populates='refresh_token')
        )
    }


@mapper_registry.mapped
# @pydantic.dataclasses.dataclass
class User(ModelMixin, UserMixin):
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
    __table__ = sa.Table(
        'user',
        mapper_registry.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('disabled', sa.Boolean, default=False),
        sa.Column('username', sa.String(80), unique=True, nullable=False),
        sa.Column('password', sa.String(512), nullable=False,
                  key='hashed_password'),
        sa.Column('role', sa.Enum(schemas.UserRoleEnum),
                  nullable=False, default=schemas.UserRoleEnum.default),
    )

    __mapper_args__ = {
        'properties': dict(
            profile=sa.orm.relationship(
                'Profile', uselist=False, back_populates='user',
                lazy='joined', cascade='all, delete-orphan'
            ),
            refresh_token=sa.orm.relationship(
                'RefreshToken', uselist=False, back_populates='user',
                lazy='joined', cascade='all, delete-orphan'
            ),
            projects=sa.orm.relationship(
                'Assignment',
                backref='user', lazy=True,
                cascade='all, delete-orphan',
            )
        )
    }
