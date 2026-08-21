from sqlalchemy.orm import Session

from app.models import Index


def create_index(db: Session, project_id: str, name: str) -> Index:
    index = Index(project_id=project_id, name=name)
    db.add(index)
    db.commit()
    db.refresh(index)
    return index


def get_index_by_name(db: Session, project_id: str, name: str) -> Index | None:
    return (
        db.query(Index)
        .filter(Index.project_id == project_id, Index.name == name)
        .first()
    )


def get_index_by_id(db: Session, project_id: str, index_id: str) -> Index | None:
    return (
        db.query(Index)
        .filter(Index.project_id == project_id, Index.id == index_id)
        .first()
    )
