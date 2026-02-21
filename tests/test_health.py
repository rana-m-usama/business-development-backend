"""Tests for root and health endpoints."""

import pytest

from app.core.config import settings


@pytest.mark.asyncio
async def test_root_returns_200(client):
    """GET / should return 200 with status ok."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_returns_200(client):
    """GET /api/v1/health should return 200 with status healthy."""
    response = await client.get(f"{settings.api_prefix}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
