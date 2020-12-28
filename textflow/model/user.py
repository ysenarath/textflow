""" User Entity """

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from textflow.service.base import database as db


class Assignment(db.Model):
    """ Project User Role Assignment Entity """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    role = db.Column(db.String(512), nullable=False, default='default')


class User(db.Model, UserMixin):
    """ User Entity """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    first_name = db.Column(db.String(512), nullable=True)
    last_name = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    projects = db.relationship('Assignment', backref='user', lazy=True)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        password = kwargs.get('password')
        self.set_password(password)

    def set_password(self, password):
        """ Set password for user. Do not set password directly.

        :param password: plain text password
        :return: this object
        """
        self.password = generate_password_hash(password)
        return self

    def verify_password(self, password):
        """ Check the password.

        :param password:
        :return:
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
