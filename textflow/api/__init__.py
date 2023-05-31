from fastapi import APIRouter

from textflow.api.routes import (
    projects,
    users,
    tokens,
    assignments,
    documents,
)

__all__ = [
    'TextFlowAPI'
]

router = APIRouter(
    prefix='/api',
)

router.include_router(tokens.router)
router.include_router(users.router)
router.include_router(projects.router)
router.include_router(assignments.router)
router.include_router(documents.router)
