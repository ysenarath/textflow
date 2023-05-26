"""User model.

This module contains the User model.

Classes
-------
User
Profile
Assignment
"""
from flask import g
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from textflow.database import db

__all__ = [
    'User',
    'Profile',
    'Assignment',
]


class Assignment(db.Model):
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), primary_key=True)
    role = db.Column(db.String(512), nullable=False, default='default')


class Profile(db.Model):
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', back_populates='profile')
    first_name = db.Column(db.String(512), nullable=True)
    last_name = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    theme = db.Column(db.String(80), nullable=False, default='light')


class User(db.Model, UserMixin):
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    projects = db.relationship(
        'Assignment', backref='user', lazy=True, cascade='all, delete-orphan')
    profile = db.relationship('Profile', uselist=False, back_populates='user',
                              lazy='joined', cascade='all, delete-orphan')
    jobs = db.relationship('BackgroundJob', backref='user', lazy='joined')

    def __init__(self, *args, **kwargs):
        """Create a new user.

        Parameters
        ----------
        *args
            Arbitrary arguments.
        **kwargs
            Arbitrary keyword arguments.
        """
        super(User, self).__init__(*args, **kwargs)
        password = kwargs.get('password')
        self.set_password(password)
        self.profile = Profile()

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
        self.password = generate_password_hash(password)
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
        return check_password_hash(self.password, password)

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
