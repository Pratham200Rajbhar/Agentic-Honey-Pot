"""
Authentication middleware for API key validation
"""

from fastapi import HTTPException, Header, Depends
from typing import Optional
import logging
import hashlib
from datetime import datetime

from .config import get_settings, Settings
from .db import db

logger = logging.getLogger(__name__)


def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(api_key.encode()).hexdigest()


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> str:
    """
    Verify the API key from request header against the database or static keys.
    """
    if not x_api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=401, detail="Missing API key. Please provide X-API-Key header."
        )

    # 1. Check legacy/static key for backward compatibility or bootstrap
    if settings.is_valid_api_key(x_api_key):
        logger.debug("Static API key validated")
        return x_api_key

    # 2. Check Database for user-created keys
    try:
        await db.connect()
        hashed_key = hash_api_key(x_api_key)

        api_key_record = await db.client.apikey.find_unique(
            where={"hashed_key": hashed_key}
        )

        if api_key_record:
            # Update last used timestamp
            await db.client.apikey.update(
                where={"id": api_key_record.id}, data={"last_used": datetime.utcnow()}
            )
            logger.debug(f"Database API key validated: {api_key_record.name}")
            return x_api_key

        partial_key = x_api_key[:8] + "..." if len(x_api_key) > 8 else "***"
        logger.warning(f"Invalid API key attempt: {partial_key}")
        raise HTTPException(status_code=401, detail="Invalid or revoked API key.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error during auth: {str(e)}")
        # If DB fails, we still allow static keys if they were checked first.
        # But here they already failed 1st check.
        raise HTTPException(
            status_code=500, detail="Internal server error during authentication."
        )
