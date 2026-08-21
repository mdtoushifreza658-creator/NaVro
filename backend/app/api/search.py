from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_project
from app.core.errors import NotFoundError
from app.models import Project
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services import index_service, search_service

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    project: Project = Depends(get_current_project),
):
    index = index_service.get_index_by_name(db, project.id, payload.index)
    if not index:
        raise NotFoundError(f"Index '{payload.index}' not found")

    page, total, took_ms = search_service.search_documents(
        db, index.id, payload.query, payload.limit, payload.offset
    )

    results = [
        SearchResultItem(id=doc.id, title=doc.title, url=doc.url, score=round(score, 4))
        for doc, score in page
    ]
    return SearchResponse(results=results, total=total, took_ms=round(took_ms, 2))
