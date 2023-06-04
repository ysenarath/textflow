import os
import typing
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import (
    Response,
    HTMLResponse,
    RedirectResponse,
)

from textflow import views
from textflow.views import tasks
from textflow.config import config

__all__ = [
    'app',
]

app = FastAPI()

AUTOBUIlD = config['textflow']['autobuild']
VIEWS_PATH = os.path.dirname(os.path.abspath(views.__file__))
DIST_PATH = os.path.join(VIEWS_PATH, 'dist')
STATIC_PATH = os.path.join(DIST_PATH, 'assets')
INDEX_PATH = os.path.join(DIST_PATH, 'index.html')

if not os.path.exists(DIST_PATH) and AUTOBUIlD:
    # Build the static files if they don't exist
    print('Building static files...', end=' ')
    tasks.executor.execute(
        ('clean', {}),
        ('build', {}),
    )
    print('[SUCCESS]')
elif not os.path.exists(DIST_PATH):
    raise FileNotFoundError(
        'The static files were not found. Please run `textflow views build`.'
    )


app.mount('/assets', StaticFiles(directory=STATIC_PATH), name='static')

public_files = StaticFiles(directory=DIST_PATH)


@app.get(
    "/{route:path}",
    response_class=typing.Union[
        Response,
        HTMLResponse,
        RedirectResponse,
    ]
)
async def index(request: Request, route: str):
    print(route)
    splits = route.split('+', maxsplit=1)
    if len(splits) == 2:
        # + is observed
        _, filename = splits
        filepath, st_res = public_files.lookup_path(filename)
        print(filename)
        if len(filepath.rstrip('/')) > len(DIST_PATH) and st_res:
            return await public_files.get_response(filename, request.scope)
    with open(INDEX_PATH) as fp:
        html = fp.read()
    response = HTMLResponse(content=html, status_code=200)
    return response
