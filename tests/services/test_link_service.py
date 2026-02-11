"""Tests for the link service module."""

from unittest.mock import patch
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.link_service import (
    generate_short_code,
    create_link,
    get_link_by_short_code,
    record_click
)
from app.models.link import Link, Click


@pytest.mark.asyncio
async def test_generate_short_code():
    """Test generating a short code."""
    # Test default length (6)
    code1 = await generate_short_code()
    assert len(code1) == 6
    assert isinstance(code1, str)

    # Test custom length
    code2 = await generate_short_code(length=8)
    assert len(code2) == 8

    # Test uniqueness (probabilistic)
    code3 = await generate_short_code()
    assert code1 != code2 != code3


@pytest.mark.asyncio
async def test_create_link(db: AsyncSession):
    """Test creating a link."""
    # Create a new link
    original_url = "https://www.fiverr.com/test-service"
    link_response = await create_link(db, original_url)

    assert link_response.original_url == original_url
    assert link_response.short_code
    assert link_response.short_url

    # Create the same link again - should return existing
    link_response2 = await create_link(db, original_url)
    assert link_response2.short_code == link_response.short_code


@pytest.mark.asyncio
async def test_get_link_by_short_code(db: AsyncSession):
    """Test retrieving a link by short code."""
    # Create a link first
    original_url = "https://www.fiverr.com/test-get-by-code"
    link_response = await create_link(db, original_url)

    # Get the link by short code
    link = await get_link_by_short_code(db, link_response.short_code)

    assert link is not None
    assert link.original_url == original_url
    assert link.short_code == link_response.short_code

    # Test with non-existent code
    non_existent = await get_link_by_short_code(db, "nonexistent")
    assert non_existent is None


@pytest.mark.asyncio
async def test_record_click(db: AsyncSession):
    """Test recording a click."""
    # Create a link first
    link_response = await create_link(db, "https://www.fiverr.com/test-record-click")

    # Get the link to get its ID
    link = await get_link_by_short_code(db, link_response.short_code)
    assert link is not None

    # Record a valid click
    ip = "192.168.1.1"
    ua = "Test User Agent"
    click = await record_click(db, link.id, ip, ua, True)

    assert click.link_id == link.id
    assert click.ip_address == ip
    assert click.user_agent == ua
    assert click.is_valid is True

    # Record an invalid click
    invalid_click = await record_click(db, link.id, ip, ua, False)
    assert invalid_click.is_valid is False