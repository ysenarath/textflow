""" TextFlow CLI """

import json
import logging
import os

import click
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from textflow import TextFlow, services
from textflow.model import *
from textflow.services import db

logger = logging.getLogger(__name__)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('-m', '--mode', default='config')
@click.option('-c', '--config_path', default=None)
@click.option('--database_url', default=None)
@click.pass_context
def cli(ctx, debug, mode, config_path, database_url):
    """Run main group commands

    :param ctx: context
    :param debug: debug mode
    :param mode: default: config
    :param config_path: path to config
    :param database_url: url to db
    :return: None
    """
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
            config['SECRET_KEY'] = os.urandom(32).decode('latin1')
        if 'WTF_CSRF_SECRET_KEY' not in config:
            config['WTF_CSRF_SECRET_KEY'] = os.urandom(32).decode('latin1')
        ctx.obj['CONFIG'] = config
        with open(config_path, 'w') as fp:
            json.dump(config, fp)


@cli.group(name='project')
def project_group():
    """Run project commands

    :return: None
    """
    pass


@cli.group(name='user')
def user_group():
    """Run user commands

    :return: None
    """
    pass


@cli.group(name='label')
def label_group():
    """Run document commands

    :return: None
    """
    pass


@cli.group(name='document')
def document_group():
    """Run label commands

    :return: None
    """
    pass


@cli.group(name='annotation')
def annotation_group():
    """Run label commands

    :return: None
    """
    pass


@project_group.command(name='create')
@click.option('-n', '--name', prompt='Project name', help='Name of project used in identifying the project by user')
@click.option('-t', '--type', prompt='Project type', help='Type of project used to identify annotation type - ' +
                                                          'Accepts one of [sequence_labeling, document_classification]')
@click.pass_context
def cli_project_create(ctx, name, type):
    """Create a project

    :param ctx: context
    :param name: Name of project used in identifying the project by user
    :param type: Type of project used to identify annotation type.
        Expected one of {sequence_labeling, document_classification}
    :return: None
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            a = Project(name=name, type=type)
            db.session.add(a)
            db.session.commit()
            logger.info('Project with name {} created successfully'.format(name))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@project_group.command(name='update')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.option('-h', '--header', help='Header html file.', default=None)
@click.pass_context
def cli_project_update(ctx, project_id, header):
    """Update project

    :param ctx: Context
    :param project_id: Project ID
    :param header: Header
    :return: None
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            a = services.get_project.ignore_user(None, project_id)
            with open(header, encoding='utf-8') as fp:
                a.guideline_template = fp.read()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@project_group.command(name='delete')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.pass_context
def cli_project_delete(ctx, project_id):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            p = services.get_project.ignore_user(None, project_id)
            if p is not None:
                if len(p.documents) > 0:
                    logger.error('Error: Unable to delete project with ID={}. '
                                 'This project is associated with one or more documents.'
                                 .format(project_id))
                else:
                    db.session.delete(p)
                    db.session.commit()
            else:
                logger.error('Error: No such project with ID={}.'.format(project_id))
        except IntegrityError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@project_group.command(name='list')
@click.pass_context
def cli_project_show(ctx):
    """project_show: -- show all projects --

    :param ctx: Context
    :return: None
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        max_len = [5, 10]
        projects = []
        for p in Project.query.all():
            projects.append([p.id, p.name])
            if max_len[0] < len(str(p.id)):
                max_len[0] = len(str(p.id))
            if max_len[1] < len(p.name):
                max_len[1] = len(p.name)
        # print table
        table_format = '{:>' + str(max_len[0]) + '} {:<' + str(max_len[0]) + '}'
        print(table_format.format('ID', 'Name'))
        for p in projects:
            print(table_format.format(*p))


@user_group.command(name='create')
@click.option('-u', '--username', prompt='Username', help='Username for login')
@click.option('-p', '--password', prompt='Password', help='Password for login')
@click.pass_context
def cli_user_create(ctx, username, password):
    """Creates user using provided args

    :param ctx: context
    :param username: Username
    :param password: Password
    :return: None
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
            logger.error('Error: {}'.format(str(e)))


@user_group.command(name='list')
@click.pass_context
def cli_user_create(ctx):
    """Creates user using provided args

    :param ctx: context
    :return: None
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            users = services.list_users()
            logger.info(users)
        except SQLAlchemyError as e:
            logger.error('Error: {}'.format(str(e)))


@user_group.command(name='update')
@click.option('-u', '--username', prompt='Username', help='Username for the account that needs the change of password')
@click.option('-p', '--password', prompt='New password', help='New password')
@click.pass_context
def cli_user_update(ctx, username, password):
    """Updates password for provided user

    :param ctx: context
    :param username: username for the account that needs the change of password
    :param password: new password
    :return:
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            users = services.filter_users(username=username)
            if len(users) == 1:
                user = users[0]
                user.set_password(password)
                db.session.commit()
                logger.info('Completed successfully.')
            else:
                logger.error('Completed with an error: User not found.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@user_group.command(name='assign')
@click.option('-u', '--username', prompt='Username', help='Username of assignee.')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID to assign.')
@click.option('-r', '--role', help='Role of user in project.', default=None)
@click.pass_context
def cli_user_assign(ctx, username, project_id, role):
    """Assign/reassign user using provided values

    :param ctx: context
    :param username: Username
    :param project_id: Project ID
    :param role: role of user in provided project
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            u = services.filter_users(username=username)
            if len(u) == 1:
                r = services.get_assignment(user_id=u[0].id, project_id=project_id)
                if r is None:
                    if role is not None:
                        a = Assignment(user_id=u[0].id, project_id=project_id, role=role)
                    else:
                        a = Assignment(user_id=u[0].id, project_id=project_id)
                    db.session.add(a)
                    db.session.commit()
                    logger.info('Completed successfully.')
                else:
                    if role is not None:
                        r.role = role
                        db.session.commit()
                        logger.info('Completed successfully.')
                    else:
                        logger.error('Error: {}'.format('unable to update existing assignment - invalid parameters'))
            else:
                logger.error('Error: {}'.format('Invalid user'))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@user_group.command(name='unassign')
@click.option('-u', '--username', prompt='Username', help='Username of assignee.')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID to assign.')
@click.pass_context
def cli_user_unassign(ctx, username, project_id):
    """Creates user using provided args

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
            status = services.remove_assignment(user_id=u[0].id, project_id=project_id)
            if status:
                logger.info('Completed successfully.')
            else:
                logger.error('Completed with an error: assignment not found.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@label_group.command(name='create')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.option('-l', '--label', prompt='Label', help='Label')
@click.option('-v', '--value', prompt='Value', help='Value')
@click.pass_context
def cli_label_create(ctx, project_id, value, label):
    """Creates user using provided args

    :param ctx: context
    :param project_id: Project ID
    :param value: Value
    :param label: Label
    :return: None
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
            logger.error('Error: {}'.format(str(e)))


@document_group.command(name='upload')
@click.option('-p', '--project_id', prompt='Project id', help='Project ident')
@click.option('-i', '--input', prompt='Input', help='Path to input file containing document')
@click.pass_context
def cli_documents_upload(ctx, project_id, input):
    """Creates user using provided args

    :param ctx: context
    :param project_id: project id
    :param input: input path
    :return: None
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            with open(input, 'r', encoding='utf-8') as fp:
                for line in fp:
                    d = json.loads(line)
                    a = Document(id_str=d['id'], text=d['text'], meta=d['meta'], project_id=project_id)
                    db.session.add(a)
                db.session.commit()
            logger.info('Completed successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@document_group.command(name='delete')
@click.option('-p', '--project_id', prompt='Project id', help='Project ident')
@click.pass_context
def cli_documents_delete(ctx, project_id):
    """Creates user using provided args

    :param ctx: context
    :param project_id: project id
    :return: None
    """
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        log = services.delete_documents.ignore_user(None, project_id)
        logger.info('Completed successfully. Deleted {} documents.'.format(log))


@annotation_group.command(name='create')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ident')
@click.option('-u', '--user_id', prompt='User ID', help='User ident')
@click.option('-d', '--document_id', prompt='Document ID', help='Document ident')
@click.option('-l', '--label', prompt='Label value', help='Label value')
@click.option('-s', '--span', prompt='Span', help='Span range; format: <start, end>')
@click.pass_context
def cli_annotation_create(ctx, project_id, document_id, user_id, label, span):
    """Creates user using provided args

    :param ctx: context
    :param project_id: project id
    :param document_id: document id
    :param user_id: user_id
    :param label: label value
    :param span: span
    """
    config = ctx.obj['CONFIG']
    label = str(label)
    span = [int(k.strip()) for k in span.split(',')]
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            doc = services.filter_document.ignore_user(None, project_id=int(project_id), id_str=document_id)
            data = {'label': {'value': label}, 'span': {'start': span[0], 'length': span[1] - span[0]}}
            services.add_annotation(project_id, user_id, doc.id, data)
            logger.info('Completed successfully.')
        except SQLAlchemyError as err:
            db.session.rollback()
            err_msg = err.args[0]
            logger.error('Error: {}'.format(err_msg))


def main():
    cli(obj={})
