"""API endpoints for link shortening and redirection."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_303_SEE_OTHER
)

from app.db.session import get_db
from app.schemas.link import (
    LinkCreate,
    LinkResponse,
    PaginatedLinkStats
)
from app.services.link_service import (
    create_link,
    get_link_by_short_code,
    record_click,
    get_links_with_stats
)
from app.services.fraud_service import validate_click

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["links"])


@router.post("/link", response_model=LinkResponse, status_code=HTTP_201_CREATED)
async def generate_short_link(
    link_data: LinkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a short link from an original URL.
    If the URL has been shortened before, return the existing short link.
    """
    logger.info(f"Generating short link for URL: {link_data.original_url}")
    return await create_link(db, str(link_data.original_url))


@router.get("/analytics", response_model=PaginatedLinkStats)
async def get_analytics(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics for all generated links.
    Results are paginated.

    Args:
        page: The page number (1-indexed)
        page_size: The number of items per page (1-100)
    """
    logger.info(f"Getting analytics (page={page}, page_size={page_size})")
    links, total = await get_links_with_stats(db, page, page_size)
    total_pages = (total + page_size - 1) // page_size  # Ceiling division

    return PaginatedLinkStats(
        links=links,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{short_code}", include_in_schema=True)
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Redirect a short link to its original URL.
    Records the click and validates it for fraud.

    The click validation takes 100ms as specified in the requirements.
    """
    logger.info(f"Processing redirect for short code: {short_code}")
    link = await get_link_by_short_code(db, short_code)
    if not link:
        logger.warning(f"Short link not found: {short_code}")
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Short link not found"
        )

    # Get IP and user agent for fraud check
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Perform fraud validation (takes 100ms as per requirement)
    is_valid = await validate_click(ip_address, user_agent)

    # Record the click
    await record_click(db, link.id, ip_address, user_agent, is_valid)

    # Redirect to original URL
    logger.info(f"Redirecting to: {link.original_url}")
    return RedirectResponse(url=link.original_url, status_code=HTTP_303_SEE_OTHER)