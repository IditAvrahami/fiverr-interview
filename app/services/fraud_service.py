"""Service for fraud detection on link clicks."""

import asyncio
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def validate_click(
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Simulates a fraud validation check that takes 100ms to complete.
    In a real application, this would implement actual fraud detection logic.

    Args:
        ip_address: The IP address of the clicker
        user_agent: The user agent of the clicker

    Returns:
        bool: True if click is valid, False if fraudulent
    """
    # Simulate processing time (100ms as per requirement)
    await asyncio.sleep(0.1)

    # For this demo, randomly mark ~10% of clicks as fraudulent
    is_valid = random.random() > 0.1

    if is_valid:
        logger.info(f"Click validated as legitimate from IP: {ip_address}")
    else:
        logger.warning(f"Click flagged as fraudulent from IP: {ip_address}")

    return is_valid