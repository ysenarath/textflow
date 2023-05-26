"""TextFlow

This module contains the main entry point to TextFlow. It is responsible for
creating the Flask app and initializing the database. It also contains the
command line interface for TextFlow.
"""
import json
import logging
import os
from os.path import expanduser

import click
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from flask import Flask

from textflow import config, tasks, views
from textflow.database import db
from textflow.auth import login_manager
from textflow.database import queries
from textflow.models import (
    Document,
    Label,
    Project,
    Task,
    User,
    Assignment,
)

logger = logging.getLogger(__name__)

__all__ = [
    'cli',
    'TextFlow',
]


class PrefixMiddleware(object):
    def __init__(self, app, prefix='') -> None:
        super().__init__()
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ['This url does not belong to the app.'.encode()]


class TextFlow:
    def __init__(self, local_config, **kwargs):
        self.local_config = local_config
        self.app = self._create_app(**kwargs)
        db.init_app(self.app)
        login_manager.init_app(self.app)
        self.celery_app = tasks.init_app(self.app)

    def _create_app(self, url_prefix=None, **kwargs):
        app = Flask(
            __name__,
            static_folder=config.static_folder,
            template_folder=config.template_folder
        )
        for bp in views.get_blueprints():
            app.register_blueprint(bp)
        # shared folder for keeping non deployment specific files
        # make sure you use a random name for each files
        shared = expanduser('~/.textflow/')
        app.config['RESOURCES_FOLDER'] = shared
        app.config['UPLOAD_FOLDER'] = os.path.join(shared, 'uploads')
        app.config['TEMPLATES'] = {}
        for k, v in self.local_config.items():
            if (k in app.config) and (app.config[k] is not None):
                app.config[k].update(v)
            else:
                app.config[k] = v
        if url_prefix is not None:
            app.wsgi_app = PrefixMiddleware(
                app.wsgi_app, prefix=url_prefix
            )
        return app

    def app_context(self):
        """Returns a context for the app."""
        return self.app.app_context()


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('-m', '--mode', default='config')
@click.option('-c', '--config_path', default=None)
@click.option('--database_url', default=None)
@click.pass_context
def cli(ctx, debug, mode, config_path, database_url):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['DEBUG'] = debug
    if mode == 'config':
        config = {}
        if config_path is None:
            config_path = os.path.join(os.getcwd(), 'config.json')
        if database_url is None:
            sqlite_uri = f'sqlite:////{os.getcwd()}/database.sqlite'
            config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
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
    pass


@cli.group(name='user')
def user_group():
    pass


@cli.group(name='label')
def label_group():
    pass


@cli.group(name='task')
def task_group():
    pass


@cli.group(name='document')
def document_group():
    pass


@cli.group(name='annotation')
def annotation_group():
    pass


@cli.group(name='dataset')
def dataset_group():
    pass


@project_group.command(name='create')
@click.option('-n', '--name', prompt='Project name',
              help='Name of project used in identifying the project by user')
@click.pass_context
def cli_project_create(ctx, name):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            a = Project(name=name)
            db.session.add(a)
            db.session.commit()
            logger.info(
                'Project with name {} created successfully'.format(name))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@project_group.command(name='update')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.option('-h', '--header', help='Header html file.', default=None)
@click.pass_context
def cli_project_update(ctx, project_id, header):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            a = queries.get_project(
                user_id=queries.ignore,
                project_id=project_id
            )
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
            p = queries.get_project(
                # user_id, project_id
                user_id=queries.ignore,
                project_id=project_id,
            )
            if p is not None:
                if len(p.documents) > 0:
                    logger.error('Error: Unable to delete project with ID={}. '
                                 'This project is associated with one or more \
                                    documents.'
                                 .format(project_id))
                else:
                    db.session.delete(p)
                    db.session.commit()
            else:
                logger.error(
                    'Error: No such project with ID={}.'.format(project_id))
        except IntegrityError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@project_group.command(name='list')
@click.pass_context
def cli_project_show(ctx):
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
        table_format = '{:>' + \
            str(max_len[0]) + '} {:<' + str(max_len[0]) + '}'
        print(table_format.format('ID', 'Name'))
        for p in projects:
            print(table_format.format(*p))


@project_group.command(name='status')
@click.option('-p', '--project_id', help='Project ident', prompt='Project ID')
@click.pass_context
def status(ctx, project_id):
    status = queries.get_project_status(project_id)
    click.echo(status)


@user_group.command(name='create')
@click.option('-u', '--username', prompt='Username', help='Username for login')
@click.option('-p', '--password', prompt='Password', help='Password for login')
@click.pass_context
def cli_user_create(ctx, username, password):
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
def cli_user_list(ctx):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            users = queries.list_users()
            logger.info(users)
        except SQLAlchemyError as e:
            logger.error('Error: {}'.format(str(e)))


@user_group.command(name='update')
@click.option('-u', '--username', prompt='Username',
              help='Username for the account that needs the change of \
                password')
@click.option('-p', '--password', prompt='New password', help='New password')
@click.pass_context
def cli_user_update(ctx, username, password):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            users = queries.filter_users(username=username)
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


@user_group.command(name='delete')
@click.option('-u', '--username', prompt='Username',
              help='Username for the account that needs the change of \
                password')
@click.pass_context
def cli_user_delete(ctx, username):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            users = queries.filter_users(username=username)
            if len(users) == 1:
                user = users[0]
                db.session.delete(user)
                db.session.commit()
                logger.info('Completed successfully.')
            else:
                logger.error('Completed with an error: User not found.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@user_group.command(name='assign')
@click.option('-u', '--username', prompt='Username',
              help='Username of assignee.')
@click.option('-p', '--project_id', prompt='Project ID',
              help='Project ID to assign.')
@click.option('-r', '--role', help='Role of user in project.',
              default=None)
@click.pass_context
def cli_user_assign(ctx, username, project_id, role):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            u = queries.filter_users(username=username)
            if len(u) == 1:
                r = queries.get_assignment(
                    user_id=u[0].id, project_id=project_id)
                if r is None:
                    if role is not None:
                        a = Assignment(
                            user_id=u[0].id, project_id=project_id, role=role)
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
                        logger.error('Error: {}'.format(
                            'unable to update existing assignment - \
                                invalid parameters'))
            else:
                logger.error('Error: {}'.format('Invalid user'))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@user_group.command(name='unassign')
@click.option('-u', '--username', prompt='Username',
              help='Username of \assignee.')
@click.option('-p', '--project_id', prompt='Project ID',
              help='Project ID to assign.')
@click.pass_context
def cli_user_unassign(ctx, username, project_id):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            u = queries.filter_users(username=username)
            status = queries.remove_assignment(
                user_id=u[0].id, project_id=project_id)
            if status:
                logger.info('Completed successfully.')
            else:
                logger.error('Completed with an error: assignment not found.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@task_group.command(name='create')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.option('-t', '--type', prompt='Task type', help='Task type')
@click.pass_context
def cli_task_create(ctx, project_id, type):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            task = Task(
                project_id=project_id,
                type=type,
            )
            db.session.add(task)
            db.session.commit()
            logger.info('Completed successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@label_group.command(name='create')
@click.option('-p', '--project_id', prompt='Project ID', help='Project ID')
@click.option('-t', '--task_id', default=None, help='Task ID')
@click.option('-l', '--label', prompt='Label', help='Label')
@click.option('-v', '--value', prompt='Value', help='Value')
@click.option('-o', '--order', help='Order', type=int, default=1)
@click.option('-c', '--color', help='Color', default=None)
@click.pass_context
def cli_label_create(ctx, project_id, task_id, value, label, order, color):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            if task_id is None:
                tasks = queries.list_tasks(
                    user_id=queries.ignore,
                    project_id=project_id
                )
                if len(tasks) > 0:
                    task = tasks[0]
                else:
                    raise ValueError(
                        f'No task found for project_id={project_id}'
                    )
            else:
                task = queries.get_task.ignore_user(task_id=task_id)
            if task is None:
                raise ValueError(f'No task found for task_id={task_id}')
            task_id = task.id
            a = Label(
                task_id=task_id,
                value=value,
                label=label,
                order=int(order),
                color=color,
            )
            db.session.add(a)
            db.session.commit()
            logger.info('Completed successfully.')
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error('Error: {}'.format(str(e)))


@document_group.command(name='upload')
@click.option('-p', '--project_id', prompt='Project id', help='Project ident')
@click.option('-i', '--input', prompt='Input',
              help='Path to input file containing document')
@click.pass_context
def cli_documents_upload(ctx, project_id, input):
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            with open(input, 'r', encoding='utf-8') as fp:
                for line in fp:
                    d = json.loads(line)
                    a = Document(id_str=d['id'], text=d['text'],
                                 meta=d['meta'], project_id=project_id)
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
    config = ctx.obj['CONFIG']
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        log = queries.delete_documents(
            user_id=queries.ignore,
            project_id=int(project_id)
        )
        logger.info(f'Completed successfully. Deleted {log} documents.')


@annotation_group.command(name='create')
@click.option('-p', '--project_id', prompt='Project ID',
              help='Project ident')
@click.option('-u', '--user_id', prompt='User ID', help='User ident')
@click.option('-d', '--document_id', prompt='Document ID',
              help='Document ident')
@click.option('-l', '--label', prompt='Label value',
              help='Label value')
@click.option('-s', '--span', prompt='Span',
              help='Span range; format: <start, end>')
@click.pass_context
def cli_annotation_create(ctx, project_id, document_id, user_id, label, span):
    config = ctx.obj['CONFIG']
    label = str(label)
    span = [int(k.strip()) for k in span.split(',')]
    tf = TextFlow(config)
    with tf.app_context():
        db.create_all()
        try:
            doc = queries.filter_document(
                user_id=queries.ignore,
                project_id=int(project_id),
                id_str=document_id
            )
            data = {'label': {'value': label}, 'span': {
                'start': span[0], 'length': span[1] - span[0]}}
            queries.add_annotation(
                # user_id, project_id, document_id, data
                user_id=user_id,
                project_id=int(project_id),
                document_id=doc.id,
                data=data
            )
            logger.info('Completed successfully.')
        except SQLAlchemyError as err:
            db.session.rollback()
            err_msg = err.args[0]
            logger.error('Error: {}'.format(err_msg))


def main():
    cli(obj={})


if __name__ == '__main__':
    cli(obj={})
