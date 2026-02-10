"""Redis async client and FastAPI dependency."""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.config import get_settings


def _create_redis_client() -> Redis:
    """Create a new Redis client from settings (no shared state)."""
    settings = get_settings()
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Yield a Redis client for the request; connection is closed when the request ends."""
    client = _create_redis_client()
    try:
        yield client
    finally:
        await client.aclose()
