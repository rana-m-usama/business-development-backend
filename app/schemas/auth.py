"""Auth schemas for request / response validation."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class UserRole(StrEnum):
    ADMIN = "admin"
    BD = "bd"
    DEVELOPER = "developer"


# ── Requests ─────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class BootstrapAdminRequest(BaseModel):
    """One-time: create the first admin when the app has no users. No auth required."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class AdminCreateUserRequest(BaseModel):
    """Admin-only: create a user who can then log in themselves."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: UserRole

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


# ── Responses ────────────────────────────────────────────────────────


class MessageResponse(BaseModel):
    message: str


class UserProfile(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    role: str
    status: str
    email_verified: bool


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile
