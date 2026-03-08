"""Security utilities: password hashing and JWT verification."""

import bcrypt
import jwt
from jwt import PyJWKClient

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def _get_jwks_client() -> PyJWKClient:
    """Lazy singleton for Supabase JWKS client (used for ES256 tokens)."""
    if not hasattr(_get_jwks_client, "_client"):
        jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _get_jwks_client._client = PyJWKClient(jwks_url, cache_keys=True)
    return _get_jwks_client._client


def decode_access_token(token: str) -> dict:
    """Decode and verify a Supabase JWT access token (HS256 or ES256).

    Raises jwt.exceptions.InvalidTokenError on any verification failure.
    """
    token = token.removeprefix("Bearer ").strip()
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "HS256")

    if alg == "ES256":
        # Supabase/GoTrue often use ES256; verify with public key from JWKS
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_aud": True},
        )
    # HS256 (symmetric secret, older or custom setup)
    return jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=["HS256"],
        audience="authenticated",
        options={"verify_aud": True},
    )
