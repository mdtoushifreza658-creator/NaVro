"""
V0 search implementation.

Deliberately the simplest thing that could work: substring matching via
Postgres ILIKE, no tokenization, no stemming, no typo tolerance. This
exists to prove the end-to-end loop (create index -> add docs -> search ->
rank -> results) before any real retrieval logic is written.

Per docs/spec.md Section 4, this is swappable behind the /search contract —
replacing this with tsvector/trgm should require no changes to the API
layer or response shape, only to this file.
"""

import time

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Document


def search_documents(
    db: Session, index_id: str, query: str, limit: int, offset: int
) -> tuple[list[tuple[Document, float]], int, float]:
    started = time.perf_counter()

    pattern = f"%{query}%"
    candidates = (
        db.query(Document)
        .filter(
            Document.index_id == index_id,
            or_(Document.title.ilike(pattern), Document.content.ilike(pattern)),
        )
        .all()
    )

    # V0 scoring heuristic: title match scores higher than content-only match.
    # This is intentionally crude — it exists so results are ordered at all,
    # not to be a real relevance model. Replaced in M1's later steps.
    scored: list[tuple[Document, float]] = []
    q_lower = query.lower()
    for doc in candidates:
        title_hit = q_lower in doc.title.lower()
        content_hit = q_lower in doc.content.lower()
        score = 0.0
        if title_hit:
            score += 0.7
        if content_hit:
            score += 0.3
        scored.append((doc, min(score, 1.0)))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    total = len(scored)
    page = scored[offset : offset + limit]

    took_ms = (time.perf_counter() - started) * 1000
    return page, total, took_ms
