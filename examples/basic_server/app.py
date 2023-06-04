""" Project Server

Serves the text annotation project.
"""
import json
import os

import uvicorn

from textflow import TextFlow

config_path = os.path.join(os.getcwd(), 'config.json')

if not os.path.exists(config_path):
    config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///textflow.db',
    }
    with open(config_path, 'w') as fp:
        json.dump(config, fp)
else:
    with open(config_path) as fp:
        config = json.load(fp)

tf = TextFlow(config, url_prefix='/textflow')

app = tf.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
