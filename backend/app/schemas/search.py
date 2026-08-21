import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


_INDEX_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


# ---- Index ----

class IndexCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not _INDEX_NAME_RE.match(v):
            raise ValueError(
                "must be 1-64 chars, lowercase letters/numbers/hyphens/underscores, "
                "and start with a letter or number"
            )
        return v


class IndexOut(BaseModel):
    id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Document ----

class DocumentCreate(BaseModel):
    id: str = Field(min_length=1, max_length=256)
    title: str = Field(min_length=1, max_length=512)
    content: str = Field(default="", max_length=100_000)
    url: str | None = Field(default=None, max_length=2048)
    metadata: dict | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if v.strip() != v or not v.strip():
            raise ValueError("must not be empty or contain leading/trailing whitespace")
        return v


class DocumentBulkCreate(BaseModel):
    documents: list[DocumentCreate] = Field(min_length=1, max_length=1000)


class DocumentOut(BaseModel):
    id: str
    title: str
    content: str
    url: str | None = None
    metadata: dict | None = Field(
        default=None, validation_alias="doc_metadata", serialization_alias="metadata"
    )
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class BulkResult(BaseModel):
    inserted: int
    errors: list[dict] = []


# ---- Search ----

class SearchRequest(BaseModel):
    index: str = Field(min_length=1, max_length=64)
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v


class SearchResultItem(BaseModel):
    id: str
    title: str
    url: str | None = None
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    total: int
    took_ms: float
