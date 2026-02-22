"""BD Profile Assignment schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.base import DBSchema


class BDProfileAssignmentCreate(BaseModel):
    user_id: UUID
    profile_id: UUID
    assigned_by: UUID


class BDProfileAssignmentUpdate(BaseModel):
    status: str | None = None
    unassigned_at: datetime | None = None


class BDProfileAssignmentResponse(DBSchema):
    user_id: UUID
    profile_id: UUID
    assigned_by: UUID
    assigned_at: datetime
    unassigned_at: datetime | None = None
    status: str
