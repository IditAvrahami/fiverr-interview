"""Pydantic models for link API."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict


# Request model for link creation
class LinkCreate(BaseModel):
    """Schema for creating a new short link."""

    original_url: HttpUrl = Field(..., description="The original URL to be shortened")


# Response model for link creation
class LinkResponse(BaseModel):
    """Schema for the response when creating a short link."""

    original_url: str
    short_url: str
    short_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Model for click data
class ClickData(BaseModel):
    """Schema for click data."""

    timestamp: datetime
    is_valid: bool

    model_config = ConfigDict(from_attributes=True)


# Monthly analytics
class MonthlyStats(BaseModel):
    """Schema for monthly statistics."""

    month: str
    valid_clicks: int
    earnings: float


# Link with analytics
class LinkStats(BaseModel):
    """Schema for link statistics."""

    original_url: str
    short_url: str
    short_code: str
    created_at: datetime
    total_clicks: int
    valid_clicks: int
    earnings: float
    monthly_stats: List[MonthlyStats]

    model_config = ConfigDict(from_attributes=True)


# Paginated response for stats
class PaginatedLinkStats(BaseModel):
    """Schema for paginated link statistics."""

    links: List[LinkStats]
    total: int
    page: int
    page_size: int
    total_pages: int