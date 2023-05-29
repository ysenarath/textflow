import math
import io
import json

import pandas as pd

from sqlalchemy.exc import SQLAlchemyError

from textflow.database import queries
from textflow.jobs.base import shared_task
from textflow.models import Document


__all__ = [
    'delete_documents',
]


@shared_task(ignore_result=False)
def delete_documents(user_id, project_id) -> int:
    delete_documents_iter = queries.delete_documents(user_id, project_id)
    for num_docs_deleted, num_docs_total in delete_documents_iter:
        progress = math.floor(num_docs_deleted * 100 / num_docs_total)
        print(f'Progress: {progress:3d}%')


@shared_task(ignore_result=False)
def upload_documents(user_id, project_id, filename, content=None) -> int:
    if content is not None:
        buffer = io.StringIO(content)
    else:
        buffer = open(filename, 'r', encoding='utf-8')
    # when buffer is a csv file
    if filename.endswith('.csv'):
        # todo: create a generator from the stream to avoid loading the
        # whole file into memory
        df = pd.read_csv(buffer)
        print('Uploading documents...', buffer, df)
        data = df.to_dict(orient='records')
    elif filename.endswith('.jsonl'):
        # create a generator to avoid loading the whole file into memory
        data = [json.loads(line) for line in buffer]
    else:
        data = None
    check = data is not None
    i = 0
    while check and i < len(data):
        d = data[i]
        if not isinstance(d, dict):
            check = False
        elif 'id' not in d and 'ID' not in d and 'Id' not in d:
            # message that the id is missing
            check = False
        elif 'text' not in d and 'TEXT' not in d and 'Text' not in d:
            # message that the text is missing
            check = False
        else:
            document = Document(
                # get source_id from id, ID or Id
                source_id=d.get('id', d.get('ID', d.get('Id'))),
                # get text from text, TEXT or Text
                text=d.get('text', d.get('TEXT', d.get('Text'))),
                meta=d,
                project_id=project_id
            )
            queries.db.session.add(document)
        i += 1
    if check:
        try:
            queries.db.session.commit()
        except SQLAlchemyError:
            queries.db.session.rollback()
    else:
        queries.db.session.rollback()
    buffer.close()
