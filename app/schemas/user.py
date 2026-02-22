"""User schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.base import DBSchema


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    status: str | None = None


class UserResponse(DBSchema):
    first_name: str
    last_name: str
    email: str
    role: str
    status: str
    email_verified: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
