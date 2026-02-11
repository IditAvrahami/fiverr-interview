"""Pydantic schemas for API request/response. Add new schemas here."""

from app.schemas.link import (
    LinkCreate,
    LinkResponse,
    ClickData,
    MonthlyStats,
    LinkStats,
    PaginatedLinkStats
)

__all__ = [
    "LinkCreate",
    "LinkResponse",
    "ClickData",
    "MonthlyStats",
    "LinkStats",
    "PaginatedLinkStats"
]
