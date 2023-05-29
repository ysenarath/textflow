""" Project Server

Serves the text annotation project.
"""
import json
import os

from textflow import TextFlow

with open(os.path.join(os.getcwd(), 'config.json')) as fp:
    config = json.load(fp)

tf = TextFlow(config, url_prefix='/textflow')

celery_app = tf.celery_app

app = tf.api.api
