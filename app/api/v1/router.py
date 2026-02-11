"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from app.api.v1 import health, links

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(links.router)


def get_router() -> APIRouter:
    """Return the v1 API router (prefix /api/v1 is added in main)."""
    return api_router
