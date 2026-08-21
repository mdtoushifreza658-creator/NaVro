"""
Minimal auth for M1: every request must carry an API key identifying its
Project, so indexes/documents/search are correctly tenant-scoped from day
one (per spec Section 2 — "no cross-project reads").

There's no POST /projects endpoint yet — that's a dashboard/M5 concern.
For now, projects are created via `scripts/seed_project.py`.
"""

from fastapi import Header, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import UnauthorizedError
from app.models import Project


def get_current_project(
    x_navro_api_key: str | None = Header(default=None, alias="X-Navro-Api-Key"),
    db: Session = Depends(get_db),
) -> Project:
    if not x_navro_api_key:
        raise UnauthorizedError("Missing API key")
    project = db.query(Project).filter(Project.api_key == x_navro_api_key).first()
    if not project:
        raise UnauthorizedError("Invalid API key")
    return project
