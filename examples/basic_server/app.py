""" Project Server

Serves the text annotation project.
"""
import json
import os

from textflow import TextFlow

with open(os.path.join(os.getcwd(), 'config.json')) as fp:
    config = json.load(fp)

tf = TextFlow(config, url_prefix='/textflow')


def create_app():
    return tf.app


celery_app = tf.app.extensions['celery']

if __name__ == '__main__':
    tf.app.config['TESTING'] = True
    tf.app.run(port=8002, debug=True)
