"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter()
api_router.include_router(health.router)


def get_router() -> APIRouter:
    """Return the v1 API router (prefix /api/v1 is added in main)."""
    return api_router
