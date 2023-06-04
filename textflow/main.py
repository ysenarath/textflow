import os
import json

import typer

from textflow import TextFlow
from textflow.database import db

app = typer.Typer()


@app.command()
def init():
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
    _ = TextFlow(config)
    db.create_all()


if __name__ == "__main__":
    app()
