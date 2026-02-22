"""Supabase client singleton."""

from functools import lru_cache

from app.core.config import settings
from supabase import Client, create_client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Return a cached Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
