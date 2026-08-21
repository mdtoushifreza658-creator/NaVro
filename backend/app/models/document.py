from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Document(Base):
    __tablename__ = "documents"

    # Developer-supplied id, unique only within its index (composite PK).
    id: Mapped[str] = mapped_column(String, primary_key=True)
    index_id: Mapped[str] = mapped_column(String, ForeignKey("indexes.id"), primary_key=True)

    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    doc_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    index: Mapped["Index"] = relationship(back_populates="documents")
