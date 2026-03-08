"""Document schemas for request/response validation."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from app.schemas.base import DBSchema


class DocumentType(StrEnum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"


class DocumentCreate(BaseModel):
    profile_id: UUID
    type: DocumentType
    title: str
    file_url: str


class DocumentUpdate(BaseModel):
    title: str | None = None
    file_url: str | None = None
    status: str | None = None


class DocumentResponse(DBSchema):
    profile_id: UUID
    type: DocumentType
    title: str
    file_url: str
    status: str
    created_at: datetime
    updated_at: datetime
