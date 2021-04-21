""" Project Server

Serves the text annotation project.
"""
import json
import os

from textflow import TextFlow

with open(os.path.join(os.getcwd(), 'config.json')) as fp:
    config = json.load(fp)

with open('./templates/projects/1/annotate.html', 'r', encoding='utf-8') as fp:
    annotate_template = fp.read()

config['templates'] = {
    'index.html': {
        'type': 'redirect.url_for',
        'value': 'login_view.login'
    },
    'annotate.html': {
        'type': 'string',
        'value': annotate_template,
        'filter': '{project.id} in [1, 2]',
    }
}

tf = TextFlow(config)

if __name__ == '__main__':
    tf.app.run(debug=True)
