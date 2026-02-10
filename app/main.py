"""FastAPI application and lifespan."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.v1.router import get_router
from app.config import get_settings
from app.db.base import Base


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Startup: engine and session factory on app.state. Shutdown: dispose engine."""
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    fastapi_app.state.engine = engine
    fastapi_app.state.async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="fiverr-interview",
    description="FastAPI skeleton with Postgres and Redis.",
    lifespan=lifespan,
)

app.include_router(get_router(), prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root: simple OK message."""
    return {"message": "OK"}
