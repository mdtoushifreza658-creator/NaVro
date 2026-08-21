from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_project
from app.core.errors import ConflictError
from app.models import Project
from app.schemas.search import IndexCreate, IndexOut
from app.services import index_service

router = APIRouter()


@router.post("/indexes", response_model=IndexOut, status_code=201)
def create_index(
    payload: IndexCreate,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
):
    existing = index_service.get_index_by_name(db, project.id, payload.name)
    if existing:
        raise ConflictError(f"Index '{payload.name}' already exists")
    return index_service.create_index(db, project.id, payload.name)
