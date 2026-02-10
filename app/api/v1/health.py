"""Health check endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.redis_client import get_redis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, str]:
    """Basic liveness: returns 200 and status ok."""
    return {"status": "ok"}


@router.get("/db")
async def health_db(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Check Postgres connectivity. Returns 503 if DB is down."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable") from None


@router.get("/redis")
async def health_redis(
    redis: Redis = Depends(get_redis),
) -> dict[str, str]:
    """Check Redis connectivity. Returns 503 if Redis is down."""
    try:
        result = await redis.ping()  # type: ignore[misc]
        if result:
            return {"status": "ok"}
        raise RuntimeError("Ping returned False")
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable") from None
