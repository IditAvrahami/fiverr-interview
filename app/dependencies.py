"""Shared FastAPI dependencies (re-export for convenience)."""

from app.db.session import get_db
from app.redis_client import get_redis

__all__ = ["get_db", "get_redis"]
