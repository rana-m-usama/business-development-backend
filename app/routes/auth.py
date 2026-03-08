"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies.auth import CurrentUser, require_role
from app.schemas.auth import (
    AdminCreateUserRequest,
    BootstrapAdminRequest,
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
    UserProfile,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
_bearer = HTTPBearer()


def _service() -> AuthService:
    return AuthService()


# ── public endpoints ──────────────────────────────────────────────────


@router.post("/bootstrap", response_model=MessageResponse, status_code=201)
def bootstrap_admin(
    data: BootstrapAdminRequest,
    svc: Annotated[AuthService, Depends(_service)],
):
    """Create the first admin user. Only works when no users exist. No auth required."""
    try:
        return svc.bootstrap_admin(data)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, svc: Annotated[AuthService, Depends(_service)]):
    return svc.login(data)


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(data: RefreshTokenRequest, svc: Annotated[AuthService, Depends(_service)]):
    return svc.refresh_token(data.refresh_token)


# ── protected endpoints ───────────────────────────────────────────────


@router.post("/logout", response_model=MessageResponse)
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    svc: Annotated[AuthService, Depends(_service)],
):
    return svc.logout(credentials.credentials)


@router.get("/me", response_model=UserProfile)
def me(current_user: CurrentUser):
    return UserProfile(
        id=current_user["id"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        email=current_user["email"],
        role=current_user["role"],
        status=current_user["status"],
        email_verified=current_user["email_verified"],
    )


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    svc: Annotated[AuthService, Depends(_service)],
):
    return svc.change_password(current_user["id"], data)


# ── admin-only: add users (user logs in themselves later) ─────────────


@router.post("/admin/users", response_model=MessageResponse, status_code=201)
def admin_create_user(
    data: AdminCreateUserRequest,
    current_user: Annotated[dict, Depends(require_role("admin"))],
    svc: Annotated[AuthService, Depends(_service)],
):
    """Create a user. They can log in with the provided email and password."""
    return svc.admin_create_user(data)
