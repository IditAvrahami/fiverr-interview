"""FastAPI application and lifespan."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.v1.router import get_router
from app.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.redis_client import close_redis


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup: ensure config and connections. Shutdown: dispose engine, close Redis."""
    get_settings()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    await close_redis()


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
