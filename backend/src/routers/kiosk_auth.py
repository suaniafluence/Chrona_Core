"""Kiosk authentication dependencies and utilities."""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models.kiosk import Kiosk
from src.security import get_password_hash, verify_password

# API Key header scheme (X-Kiosk-API-Key)
api_key_header = APIKeyHeader(name="X-Kiosk-API-Key", auto_error=False)


def generate_kiosk_api_key() -> str:
    """Generate a secure random API key for kiosks.

    Returns:
        32-character URL-safe random string
    """
    return secrets.token_urlsafe(32)


def hash_kiosk_api_key(api_key: str) -> str:
    """Hash a kiosk API key using bcrypt.

    Args:
        api_key: Plain API key string

    Returns:
        Bcrypt hash of the API key
    """
    return get_password_hash(api_key)


def verify_kiosk_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verify a kiosk API key against its hash.

    Args:
        plain_api_key: Plain API key from request
        hashed_api_key: Hashed API key from database

    Returns:
        True if API key matches, False otherwise
    """
    return verify_password(plain_api_key, hashed_api_key)


async def get_current_kiosk(
    api_key: Annotated[str | None, Depends(api_key_header)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Kiosk:
    """Dependency to get the current authenticated kiosk.

    Args:
        api_key: API key from X-Kiosk-API-Key header
        session: Database session

    Returns:
        Authenticated Kiosk object

    Raises:
        HTTPException 401: Missing or invalid API key
        HTTPException 403: Kiosk is not active
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key (X-Kiosk-API-Key header required)",
        )

    # Query all kiosks and verify API key (since we can't query by hash)
    # This is acceptable because the number of kiosks is small (~25 max)
    result = await session.execute(select(Kiosk).where(Kiosk.api_key_hash.isnot(None)))
    kiosks = result.scalars().all()

    authenticated_kiosk = None
    for kiosk in kiosks:
        if verify_kiosk_api_key(api_key, kiosk.api_key_hash):
            authenticated_kiosk = kiosk
            break

    if not authenticated_kiosk:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if not authenticated_kiosk.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kiosk is not active",
        )

    return authenticated_kiosk
