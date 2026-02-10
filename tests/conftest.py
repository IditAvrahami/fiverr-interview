"""Pytest fixtures: app and async HTTP client."""

from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def app_instance() -> FastAPI:
    """Return the FastAPI app."""
    return app


@pytest.fixture
async def client(app_instance: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing the app."""
    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
