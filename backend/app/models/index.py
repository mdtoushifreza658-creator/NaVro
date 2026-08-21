import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Index(Base):
    __tablename__ = "indexes"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_index_project_name"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: f"idx_{uuid.uuid4().hex[:12]}"
    )
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship(back_populates="indexes")
    documents: Mapped[list["Document"]] = relationship(back_populates="index", cascade="all, delete-orphan")
