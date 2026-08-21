from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_project
from app.core.errors import NotFoundError
from app.models import Project
from app.schemas.search import DocumentCreate, DocumentBulkCreate, DocumentOut, BulkResult
from app.services import index_service, document_service

router = APIRouter()


def _get_index_or_404(db: Session, project: Project, index_id: str):
    index = index_service.get_index_by_id(db, project.id, index_id)
    if not index:
        raise NotFoundError(f"Index '{index_id}' not found")
    return index


@router.post("/indexes/{index_id}/documents", response_model=DocumentOut, status_code=201)
def add_document(
    index_id: str,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
):
    _get_index_or_404(db, project, index_id)
    doc = document_service.upsert_document(db, index_id, payload)
    return doc


@router.post("/indexes/{index_id}/documents/bulk", response_model=BulkResult)
def add_documents_bulk(
    index_id: str,
    payload: DocumentBulkCreate,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
):
    _get_index_or_404(db, project, index_id)
    inserted, errors = document_service.bulk_upsert_documents(db, index_id, payload.documents)
    return BulkResult(inserted=inserted, errors=errors)


@router.delete("/indexes/{index_id}/documents/{doc_id}", status_code=204)
def delete_document(
    index_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
):
    _get_index_or_404(db, project, index_id)
    deleted = document_service.delete_document(db, index_id, doc_id)
    if not deleted:
        raise NotFoundError(f"Document '{doc_id}' not found")
