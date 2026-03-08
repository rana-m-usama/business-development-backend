"""Authentication service — all auth business logic lives here.

Uses the Supabase Admin SDK for user management and direct REST calls
to GoTrue for user-facing operations (login, logout, refresh) to avoid
polluting the shared client's session state in a concurrent backend.
"""

from datetime import UTC, datetime

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.core.supabase import get_supabase_client
from app.schemas.auth import (
    AdminCreateUserRequest,
    BootstrapAdminRequest,
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenResponse,
    TokenResponse,
    UserProfile,
    UserRole,
)

_GOTRUE_BASE = f"{settings.supabase_url}/auth/v1"
_API_HEADERS = {
    "apikey": settings.supabase_service_role_key,
    "Content-Type": "application/json",
}


class AuthService:
    """Stateless service — safe to instantiate per request."""

    def __init__(self) -> None:
        self.client = get_supabase_client()

    # ── helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _gotrue_request(
        method: str,
        path: str,
        *,
        json: dict | None = None,
        bearer_token: str | None = None,
    ) -> dict:
        """Call a GoTrue REST endpoint and return the parsed response."""
        headers = {**_API_HEADERS}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        resp = httpx.request(method, f"{_GOTRUE_BASE}{path}", json=json, headers=headers, timeout=30)

        if resp.status_code >= 400:
            body = resp.json() if resp.content else {}
            detail = body.get("error_description") or body.get("msg") or body.get("error") or "Auth request failed"
            raise HTTPException(status_code=resp.status_code, detail=detail)

        return resp.json() if resp.content else {}

    def _get_user_row(self, *, user_id: str | None = None, email: str | None = None) -> dict:
        """Fetch a single row from the custom users table."""
        query = self.client.table("users").select("*")
        if user_id:
            query = query.eq("id", user_id)
        elif email:
            query = query.eq("email", email)
        else:
            raise ValueError("Provide user_id or email")

        response = query.single().execute()
        return response.data

    # ── bootstrap: first admin when no users exist ───────────────────────

    def bootstrap_admin(self, data: BootstrapAdminRequest) -> MessageResponse:
        """Create the first admin. Only works when the users table is empty. No auth required."""
        response = self.client.table("users").select("id").limit(1).execute()
        if response.data and len(response.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bootstrap only allowed when no users exist. Use POST /auth/admin/users as an admin.",
            )
        return self.admin_create_user(
            AdminCreateUserRequest(
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                password=data.password,
                role=UserRole.ADMIN,
            )
        )

    # ── admin: add user (user logs in themselves later) ────────────────

    def admin_create_user(self, data: AdminCreateUserRequest) -> MessageResponse:
        """Create a user as admin. User can log in with the given password immediately."""
        # 1. Create in Supabase Auth with email pre-confirmed (no verification required)
        try:
            auth_user = self.client.auth.admin.create_user(
                {
                    "email": data.email,
                    "password": data.password,
                    "email_confirm": True,
                    "user_metadata": {
                        "first_name": data.first_name,
                        "last_name": data.last_name,
                        "role": str(data.role),
                    },
                }
            )
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        # Handle both object and dict-like response from Supabase client
        user_obj = getattr(auth_user, "user", None) or (auth_user if isinstance(auth_user, dict) else {}).get("user")
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create auth user (no user in response)",
            )
        auth_uid = str(getattr(user_obj, "id", None) or user_obj.get("id", ""))
        if not auth_uid:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get auth user id",
            )

        # 2. Insert into custom users table (email_verified=True so they can login without verifying)
        try:
            self.client.table("users").insert(
                {
                    "id": auth_uid,
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                    "email": data.email,
                    "password_hash": hash_password(data.password),
                    "role": str(data.role),
                    "status": "active",
                    "email_verified": True,
                }
            ).execute()
        except Exception as exc:
            self.client.auth.admin.delete_user(auth_uid)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user record: {exc}",
            ) from exc

        return MessageResponse(message="User created. They can log in with the provided email and password.")

    # ── login ─────────────────────────────────────────────────────────

    def login(self, data: LoginRequest) -> TokenResponse:
        # 1. Authenticate via GoTrue (returns tokens)
        auth_data = self._gotrue_request(
            "POST",
            "/token?grant_type=password",
            json={"email": data.email, "password": data.password},
        )

        # 2. Fetch custom user row for status / role checks
        try:
            user_row = self._get_user_row(email=data.email)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User record not found",
            ) from exc

        if user_row["status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user_row['status']}. Please contact support.",
            )

        if not user_row["email_verified"]:
            # Sync from Supabase Auth — they might have verified via the link
            auth_user_obj = auth_data.get("user", {})
            if auth_user_obj.get("email_confirmed_at"):
                self.client.table("users").update({"email_verified": True}).eq("id", user_row["id"]).execute()
                user_row["email_verified"] = True
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Email not verified. Please verify your email before logging in.",
                )

        # 3. Update last_login_at
        self.client.table("users").update({"last_login_at": datetime.now(UTC).isoformat()}).eq(
            "id", user_row["id"]
        ).execute()

        return TokenResponse(
            access_token=auth_data["access_token"],
            refresh_token=auth_data["refresh_token"],
            expires_in=auth_data["expires_in"],
            user=UserProfile(
                id=user_row["id"],
                first_name=user_row["first_name"],
                last_name=user_row["last_name"],
                email=user_row["email"],
                role=user_row["role"],
                status=user_row["status"],
                email_verified=user_row["email_verified"],
            ),
        )

    # ── logout ────────────────────────────────────────────────────────

    def logout(self, access_token: str) -> MessageResponse:
        self._gotrue_request("POST", "/logout", bearer_token=access_token)
        return MessageResponse(message="Logged out successfully.")

    # ── token refresh ─────────────────────────────────────────────────

    def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        data = self._gotrue_request(
            "POST",
            "/token?grant_type=refresh_token",
            json={"refresh_token": refresh_token},
        )
        return RefreshTokenResponse(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type="bearer",
            expires_in=data["expires_in"],
        )

    # ── password (change when logged in) ───────────────────────────────

    def change_password(self, user_id: str, data: ChangePasswordRequest) -> MessageResponse:
        # 1. Verify current password against custom table
        user_row = self._get_user_row(user_id=user_id)
        if not verify_password(data.current_password, user_row["password_hash"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        # 2. Update in Supabase Auth
        try:
            self.client.auth.admin.update_user_by_id(user_id, {"password": data.new_password})
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        # 3. Update password_hash in custom users table
        self.client.table("users").update({"password_hash": hash_password(data.new_password)}).eq(
            "id", user_id
        ).execute()

        return MessageResponse(message="Password changed successfully.")
