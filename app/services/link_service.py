"""Service for URL shortening and link tracking."""

import random
import string
from typing import Optional, List, Tuple
from datetime import datetime
import logging

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from app.models.link import Link, Click
from app.schemas.link import LinkResponse, LinkStats, MonthlyStats
from app.config import get_settings

# Set up logging
logger = logging.getLogger(__name__)


async def generate_short_code(length: int = 6) -> str:
    """Generate a random short code for the URL.

    Args:
        length: The length of the short code (default: 6)

    Returns:
        A random string of the specified length
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


async def create_link(db: AsyncSession, original_url: str) -> LinkResponse:
    """Create a new short link or return an existing one.

    Args:
        db: The database session
        original_url: The original URL to shorten

    Returns:
        A LinkResponse object containing the original URL and short link information
    """
    # Check if URL already exists
    stmt = select(Link).where(Link.original_url == original_url)
    result = await db.execute(stmt)
    existing_link = result.scalar_one_or_none()

    if existing_link:
        logger.info(f"Found existing link for URL: {original_url}")
        settings = get_settings()
        base_url = settings.BASE_URL
        return LinkResponse(
            original_url=existing_link.original_url,
            short_url=f"{base_url}/{existing_link.short_code}",
            short_code=existing_link.short_code,
            created_at=existing_link.created_at
        )

    # Create new link
    short_code = await generate_short_code()

    # Ensure code doesn't already exist
    while True:
        stmt = select(Link).where(Link.short_code == short_code)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            break
        short_code = await generate_short_code()

    logger.info(f"Creating new short link for URL: {original_url}")
    new_link = Link(original_url=original_url, short_code=short_code)
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)

    settings = get_settings()
    base_url = settings.BASE_URL
    return LinkResponse(
        original_url=new_link.original_url,
        short_url=f"{base_url}/{new_link.short_code}",
        short_code=new_link.short_code,
        created_at=new_link.created_at
    )


async def get_link_by_short_code(db: AsyncSession, short_code: str) -> Optional[Link]:
    """Get a link by its short code.

    Args:
        db: The database session
        short_code: The short code to look up

    Returns:
        The Link object if found, None otherwise
    """
    stmt = select(Link).where(Link.short_code == short_code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def record_click(
    db: AsyncSession,
    link_id: int,
    ip_address: Optional[str],
    user_agent: Optional[str],
    is_valid: bool
) -> Click:
    """Record a click on a link.

    Args:
        db: The database session
        link_id: The ID of the link that was clicked
        ip_address: The IP address of the clicker
        user_agent: The user agent of the clicker
        is_valid: Whether the click passed fraud validation

    Returns:
        The created Click object
    """
    click = Click(
        link_id=link_id,
        ip_address=ip_address,
        user_agent=user_agent,
        is_valid=is_valid
    )
    db.add(click)
    await db.commit()
    await db.refresh(click)

    logger.info(
        f"Recorded click for link_id={link_id}, is_valid={is_valid}"
    )
    return click


async def get_links_with_stats(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10
) -> Tuple[List[LinkStats], int]:
    """Get paginated links with their statistics.

    Args:
        db: The database session
        page: The page number (1-indexed)
        page_size: The number of items per page

    Returns:
        A tuple of (links with stats, total links count)
    """
    # Count total links
    count_stmt = select(func.count()).select_from(Link)
    result = await db.execute(count_stmt)
    total_links = result.scalar_one()

    # Get paginated links
    offset = (page - 1) * page_size
    stmt = select(Link).order_by(Link.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    links = result.scalars().all()

    settings = get_settings()
    base_url = settings.BASE_URL
    credit_per_click = settings.CREDIT_PER_CLICK

    link_stats = []
    for link in links:
        # Get total clicks
        total_stmt = select(func.count()).select_from(Click).where(Click.link_id == link.id)
        result = await db.execute(total_stmt)
        total_clicks = result.scalar_one()

        # Get valid clicks
        valid_stmt = select(func.count()).select_from(Click).where(
            Click.link_id == link.id,
            Click.is_valid == True
        )
        result = await db.execute(valid_stmt)
        valid_clicks = result.scalar_one()

        # Calculate earnings (5 cents per valid click)
        earnings = valid_clicks * (credit_per_click / 100)  # Convert cents to dollars

        # Get monthly breakdown using raw SQL for better date handling
        # Check if we're using SQLite (test environment) or PostgreSQL
        if "sqlite" in str(db.bind.engine.url):
            # SQLite version - use strftime instead of TO_CHAR
            month_stmt = text("""
                SELECT
                    strftime('%Y-%m', created_at) as month,
                    SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) as valid_clicks
                FROM clicks
                WHERE link_id = :link_id
                GROUP BY month
                ORDER BY month
            """)
        else:
            # PostgreSQL version
            month_stmt = text("""
                SELECT
                    TO_CHAR(created_at, 'YYYY-MM') as month,
                    COUNT(*) FILTER (WHERE is_valid = TRUE) as valid_clicks
                FROM clicks
                WHERE link_id = :link_id
                GROUP BY month
                ORDER BY month
            """)

        result = await db.execute(month_stmt, {"link_id": link.id})
        monthly_data = result.fetchall()

        monthly_stats = [
            MonthlyStats(
                month=month,
                valid_clicks=valid_clicks_count,
                earnings=valid_clicks_count * (credit_per_click / 100)
            )
            for month, valid_clicks_count in monthly_data
        ]

        link_stats.append(LinkStats(
            original_url=link.original_url,
            short_url=f"{base_url}/{link.short_code}",
            short_code=link.short_code,
            created_at=link.created_at,
            total_clicks=total_clicks,
            valid_clicks=valid_clicks,
            earnings=earnings,
            monthly_stats=monthly_stats
        ))

    return link_stats, total_links