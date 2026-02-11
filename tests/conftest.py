"""Pytest fixtures: app, database, and async HTTP client."""

from collections.abc import AsyncGenerator
import asyncio
from typing import Iterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base import Base
from app.config import get_settings
# Import models to ensure they are registered with Base.metadata before creating tables
from app.models import Link, Click

# Use SQLite for testing with a file-based database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a SQLAlchemy engine for testing with session scope."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool
    )

    # Print out metadata to debug
    print("Tables to be created:", Base.metadata.tables.keys())

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    """Return a SQLAlchemy session for testing."""
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    async with session_factory() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture
def app_instance() -> FastAPI:
    """Return the FastAPI app."""
    settings = get_settings()
    app.state.test_mode = True
    return app


@pytest.fixture
async def client(app_instance: FastAPI, db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing the app."""
    # Override database session dependency
    from app.db.session import get_db

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides = {}
