from celery import Celery, Task, shared_task as celery_shared_task
from flask import Flask, current_app

from textflow.database import queries
from textflow.models import BackgroundJob

__all__ = [
    'init_app',
    'shared_task',
]


class SharedTask(object):
    def __init__(self, func, *args, **kwargs) -> None:
        self.name = func.__name__
        self.task = celery_shared_task(*args, **kwargs)(func)

    def delay(self, *args, **kwargs):
        job = self.task.delay(*args, **kwargs)
        job_hash = f'{self.name}(?)'
        job = BackgroundJob(
            id=job.id,
            user_id=kwargs.get('user_id'),
            project_id=kwargs.get('project_id'),
            hash=job_hash,
        )
        # add job to the database
        queries.db.session.add(job)
        # commit the changes
        queries.db.session.commit()
        return job


def shared_task(*args, **kwargs) -> SharedTask:
    """Decorator for celery shared task.

    Parameters
    ----------
    *args
        Positional arguments for celery shared task.
    **kwargs
        Keyword arguments for celery shared task.

    Returns
    -------
    TaskBase
        Task base object.
    """
    def decorator(func):
        return SharedTask(func, *args, **kwargs)
    return decorator


def celery_init_app(app: Flask) -> Celery:
    """Initialize celery application.

    Parameters
    ----------
    app : Flask
        Flask application.

    Returns
    -------
    Celery
        Celery application.
    """
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config['CELERY'])
    celery_app.set_default()
    app.extensions['celery'] = celery_app
    return celery_app


def init_app(app: Flask, type='celery') -> Celery:
    """Initialize tasks with celery application.

    Parameters
    ----------
    app : Flask
        Flask application.
    type : str, optional
        Type of task application, by default 'celery'

    Returns
    -------
    Celery
        Celery application.
    """
    if type.lower() == 'celery':
        return celery_init_app(app)
    raise NotImplementedError(f'Not implemented {type} type.')
