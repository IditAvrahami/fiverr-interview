"""Tests for the fraud validation service."""

import asyncio
import time
import pytest

from app.services.fraud_service import validate_click


@pytest.mark.asyncio
async def test_validate_click_takes_100ms():
    """Test that the validate_click function takes 100ms to execute."""
    start_time = time.time()
    result = await validate_click("192.168.1.1", "Test User Agent")
    end_time = time.time()
    duration = (end_time - start_time) * 1000  # Convert to milliseconds

    # Check that the function takes approximately 100ms (with some tolerance)
    assert 95 <= duration <= 150, f"Duration was {duration}ms instead of ~100ms"
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_validate_click_returns_bool():
    """Test that validate_click returns a boolean value."""
    # Run multiple times to ensure we get a mix of True and False
    results = [await validate_click() for _ in range(100)]

    # Verify all results are boolean
    assert all(isinstance(r, bool) for r in results)

    # Verify we get at least some True and some False values
    # (This is probabilistic but highly unlikely to fail)
    assert any(results) and not all(results), "Expected both True and False results"