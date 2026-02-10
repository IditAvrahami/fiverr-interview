"""Tests for health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    """GET /api/v1/health returns 200 and status ok."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


@pytest.mark.asyncio
async def test_root(client: AsyncClient) -> None:
    """GET / returns 200 and message OK."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json().get("message") == "OK"
