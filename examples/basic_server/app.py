""" Project Server

Serves the text annotation project.
"""
import json
import os

import uvicorn

from textflow import TextFlow

with open(os.path.join(os.getcwd(), 'config.json')) as fp:
    config = json.load(fp)

tf = TextFlow(config)

if __name__ == "__main__":
    uvicorn.run(tf.api, host="0.0.0.0", port=8000)
