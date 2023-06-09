import os
import json

import typer

from textflow import TextFlow
from textflow.database import db

app = typer.Typer()


@app.command()
def init():
    cwd = os.getcwd()
    config_path = os.path.join(cwd, 'config.json')
    if not os.path.exists(config_path):
        config = {
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{cwd}/textflow.db',
        }
        with open(config_path, 'w') as fp:
            json.dump(config, fp)
    else:
        with open(config_path) as fp:
            config = json.load(fp)
    _ = TextFlow(config)
    db.create_all()


if __name__ == "__main__":
    app()
