"""
NaVro API — entrypoint.

M1: the full Create Index -> Add Documents -> Search -> Rank -> Results
loop, per docs/spec.md. Search itself is the V0 naive ILIKE implementation
in app/services/search_service.py — swappable, not final.
"""

from fastapi import FastAPI

from app.core.db import Base, engine
from app.core.errors import register_exception_handlers
from app import models  # noqa: F401 — ensures models are registered on Base
from app.api import indexes, documents, search

# M1: create tables directly from models. Replace with Alembic migrations
# once the schema needs to evolve without dropping data.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NaVro API",
    description="Embeddable search infrastructure — V1",
    version="0.2.0",
)

register_exception_handlers(app)

app.include_router(indexes.router, tags=["indexes"])
app.include_router(documents.router, tags=["documents"])
app.include_router(search.router, tags=["search"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "navro-api", "version": "0.2.0"}
