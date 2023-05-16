from celery import Celery, Task
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config['CELERY'])
    celery_app.set_default()
    app.extensions['celery'] = celery_app
    return celery_app


def init_app(app: Flask, type='celery') -> Celery:
    if type == 'celery':
        app.config.from_mapping(
            CELERY=dict(
                broker_url="redis://localhost",
                result_backend="redis://localhost",
                task_ignore_result=True,
            ),
        )
        return celery_init_app(app)
    raise NotImplementedError(f'Not implemented {type} type.')
