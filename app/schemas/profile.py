"""Profile schemas for request/response validation."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr

from app.schemas.base import DBSchema


class ProfileType(StrEnum):
    LINKEDIN = "linkedin"
    UPWORK = "upwork"
    INDEED = "indeed"


class ProfileCreate(BaseModel):
    first_name: str
    last_name: str
    type: ProfileType
    email: EmailStr
    link: str | None = None
    country: str | None = None


class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    link: str | None = None
    country: str | None = None
    status: str | None = None


class ProfileResponse(DBSchema):
    first_name: str
    last_name: str
    type: ProfileType
    email: str
    link: str | None = None
    country: str | None = None
    status: str
    created_at: datetime
