from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Document


def upsert_document(db: Session, index_id: str, doc_in) -> Document:
    """Insert a document, or overwrite if the same id already exists in this index."""
    existing = (
        db.query(Document)
        .filter(Document.index_id == index_id, Document.id == doc_in.id)
        .first()
    )
    if existing:
        existing.title = doc_in.title
        existing.content = doc_in.content
        existing.url = doc_in.url
        existing.doc_metadata = doc_in.metadata
        db.commit()
        db.refresh(existing)
        return existing

    doc = Document(
        id=doc_in.id,
        index_id=index_id,
        title=doc_in.title,
        content=doc_in.content,
        url=doc_in.url,
        doc_metadata=doc_in.metadata,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def bulk_upsert_documents(db: Session, index_id: str, docs_in: list) -> tuple[int, list[dict]]:
    inserted = 0
    errors = []
    for doc_in in docs_in:
        try:
            upsert_document(db, index_id, doc_in)
            inserted += 1
        except IntegrityError as e:
            db.rollback()
            errors.append({"id": doc_in.id, "error": str(e.orig)})
    return inserted, errors


def delete_document(db: Session, index_id: str, doc_id: str) -> bool:
    doc = (
        db.query(Document)
        .filter(Document.index_id == index_id, Document.id == doc_id)
        .first()
    )
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
