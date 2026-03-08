"""Application schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.base import DBSchema


class ApplicationCreate(BaseModel):
    profile_id: UUID
    resume_id: UUID | None = None
    cover_letter_id: UUID | None = None
    bidder_id: UUID
    assignee_id: UUID | None = None
    company_name: str
    job_title: str
    job_url: str | None = None
    location: str | None = None
    job_type: str | None = None
    priority: str | None = None
    is_global: bool = False
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    resume_id: UUID | None = None
    cover_letter_id: UUID | None = None
    assignee_id: UUID | None = None
    job_url: str | None = None
    location: str | None = None
    job_type: str | None = None
    priority: str | None = None
    is_global: bool | None = None
    current_stage: str | None = None
    interview_date: datetime | None = None
    has_assessment: bool | None = None
    assessment_status: str | None = None
    notes: str | None = None


class ApplicationResponse(DBSchema):
    profile_id: UUID
    resume_id: UUID | None = None
    cover_letter_id: UUID | None = None
    bidder_id: UUID
    assignee_id: UUID | None = None
    company_name: str
    job_title: str
    job_url: str | None = None
    location: str | None = None
    job_type: str | None = None
    priority: str | None = None
    is_global: bool
    current_stage: str
    interview_date: datetime | None = None
    has_assessment: bool
    assessment_status: str | None = None
    applied_date: datetime
    created_at: datetime
    notes: str | None = None
