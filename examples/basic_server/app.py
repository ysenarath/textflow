""" Project Server

Serves the text annotation project.
"""
import json
import os

from textflow import TextFlow

with open(os.path.join(os.getcwd(), 'config.json')) as fp:
    config = json.load(fp)

config['templates'] = {}

with open('./templates/projects/1/annotate.html', 'r', encoding='utf-8') as fp:
    config['templates']['projects/1/annotate.html'] = fp.read()

tf = TextFlow(config)

if __name__ == '__main__':
    tf.app.run(debug=True)
