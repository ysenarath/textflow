"""Routes for assignments."""
import typing
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from textflow.api.dependencies import (
    get_current_active_user,
    roles_required,
    get_session,
)

from textflow import schemas
from textflow.database import op

__all__ = [
    'router',
]


router = APIRouter(
    prefix='/projects/{project_id}/documents',
    tags=['Documents'],
    dependencies=[Depends(get_current_active_user)],
    responses={
        404: {'description': 'Not found'}
    },
)


@router.put('/')
async def create_document(
    project_id: int,
    document: schemas.DocumentBase,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required({'admin'})),
):
    document = schemas.Document(
        project_id=project_id, **document.dict(), id=None
    )
    document = op.create_document(session, doc=document)
    return document


@router.put('/')
async def get_documents_of_project(
    project_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required({'admin'})),
):
    documents = op.list_documents_by(session, project_id=project_id)
    return documents


@router.put('/{document_id}')
async def get_document(
    document_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(roles_required({'admin'})),
):
    documents = op.get_document(session, document_id=document_id)
    return documents
