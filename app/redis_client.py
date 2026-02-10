"""Redis async client and FastAPI dependency."""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.config import get_settings

_redis: Redis | None = None


def get_redis_client() -> Redis:
    """Build Redis client from settings (call once at startup)."""
    settings = get_settings()
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Yield Redis client for FastAPI dependency injection."""
    global _redis
    if _redis is None:
        _redis = get_redis_client()
    yield _redis


async def close_redis() -> None:
    """Close Redis connection (call on shutdown)."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
