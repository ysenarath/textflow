import os
from invoke import task, Collection
from invoke.executor import Executor

from textflow import views


VIEWS_PATH = os.path.dirname(os.path.abspath(views.__file__))
DIST_PATH = os.path.join(VIEWS_PATH, 'dist')


@task
def clean(c):
    c.run(f'rm -rf {DIST_PATH}')


@task
def build(c):
    # update config file before building
    c.run(f'npm --prefix {VIEWS_PATH} run build')


collection = Collection('textflow.views.tasks')
collection.add_task(clean)
collection.add_task(build)
executor = Executor(collection)
