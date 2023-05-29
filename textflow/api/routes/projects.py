'''Project router.'''
from fastapi import APIRouter, Depends

from textflow.api.dependencies import get_current_active_user
from textflow.models import Project

__all__ = [
    'router',
]

router = APIRouter(
    prefix='/projects',
    tags=['projects'],
    dependencies=[Depends(get_current_active_user)],
    responses={
        404: {'description': 'Not found'}
    },
)


@router.get("/{project_id}", response_model=Project)
async def read_item(project_id: int):
    return {
        'id': project_id,
        'name': 'Foo',
        'description': 'The pretender',
    }


@router.post('/')
async def create_project(project: Project):
    return project


@router.put(
    '/{project_id}',
    responses={403: {'description': 'Operation forbidden'}},
)
async def update_project(project_id: int, project: Project):
    # if project_id not in fake_db:
    #     raise HTTPException(status_code=404, detail='Item not found')
    return project
