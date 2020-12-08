import json
import logging
import os

import click
from sqlalchemy.exc import SQLAlchemyError

from textflow import TextFlow, services
from textflow.db import db
from textflow.model import *

logger = logging.getLogger(__name__)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('-m', '--mode', default='config')
@click.option('-c', '--config_path', default=None)
@click.option('--database_url', default=None)
@click.pass_context
def cli(ctx, debug, mode, config_path, database_url):
    """ Run main group commands """
    ctx.obj['DEBUG'] = debug
    if mode == 'config':
        config = {}
        if config_path is None:
            config_path = os.path.join(os.getcwd(), 'config.json')
        if database_url is None:
            config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}/database.sqlite'.format(os.getcwd())
        else:
            config['SQLALCHEMY_DATABASE_URI'] = database_url
        if os.path.exists(config_path):
            with open(config_path) as fp:
                config.update(json.load(fp))
        if 'SQLALCHEMY_TRACK_MODIFICATIONS' not in config:
            config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        if 'SECRET_KEY' not in config:
            config['SECRET_KEY'] = str(os.urandom(32))
        if 'WTF_CSRF_SECRET_KEY' not in config:
            config['WTF_CSRF_SECRET_KEY'] = str(os.urandom(32))
        ctx.obj['CONFIG'] = config
        with open(config_path, 'w') as fp:
            json.dump(config, fp)


@cli.group(name='project')
def project_group():
    """ Run project commands """
    pass


@cli.group(name='user')
def user_group():
    """ Run user commands """
    pass


@cli.group(name='label')
def label_group():
    """ Run document commands """
    pass


@cli.group(name='document')
def document_group():
    """ Run label commands """
    pass


@project_group.command(name='create')
@click.pass_context
def cli_project_create(ctx):
    """ project_create """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            a = Project(
                name=input('Enter the name of project: '),
                type=input('Enter type of project: '),
            )
            db.session.add(a)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(str(e))


@user_group.command(name='create')
@click.option('-u', '--username', prompt='Your username', help='Username for login.')
@click.option('-p', '--password', prompt='Your password', help='Password for login.')
@click.pass_context
def cli_user_create(ctx, username, password):
    """ Creates user using provided args

    :param ctx: context
    :param username: Username
    :param password: Password
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            a = User(username=username, password=password)
            db.session.add(a)
            db.session.commit()
            logger.info('Completed successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Completed with an error: {}'.format(str(e)))


@user_group.command(name='assign')
@click.option('-u', '--username', prompt='Your username', help='Username for login.')
@click.option('-p', '--project_id', prompt='Your password', help='Project ident. to assign.')
@click.pass_context
def cli_user_assign(ctx, username, project_id):
    """ Creates user using provided args

    :param ctx: context
    :param username: Username
    :param project_id: Project ID
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            u = services.filter_users(username=username)
            a = Assignment(user_id=u[0].id, project_id=project_id)
            db.session.add(a)
            db.session.commit()
            logger.info('Completed successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Completed with an error: {}'.format(str(e)))


@label_group.command(name='create')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.option('-l', '--label', prompt='Label', help='Label')
@click.option('-v', '--value', prompt='Value', help='Value')
@click.pass_context
def cli_label_create(ctx, project_id, value, label):
    """ Creates user using provided args

    :param ctx: context
    :param project_id: Project ID
    :param value: Value
    :param label: Label
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            a = Label(project_id=project_id, value=value, label=label)
            db.session.add(a)
            db.session.commit()
            logger.info('Completed successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Completed with an error: {}'.format(str(e)))


@document_group.command(name='upload')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.option('-i', '--input', prompt='Project ID', help='Project ID')
@click.pass_context
def cli_documents_upload(ctx, project_id, input):
    """ Creates user using provided args

    :param ctx: context
    :param project_id: project id
    :param input: input path
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            for d in json.load(open(input)):
                a = Document(id=d['id'], text=d['text'], meta=d['meta'], project_id=project_id)
                db.session.add(a)
            db.session.commit()
            logger.info('Completed successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Completed with an error: {}'.format(str(e)))


if __name__ == '__main__':
    cli(obj={})
