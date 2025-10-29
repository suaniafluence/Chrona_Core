"""Middleware to extract client IP address for kiosk identification."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models.kiosk import Kiosk


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request.

    Handles X-Forwarded-For header for proxied requests.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address (IPv4 or IPv6)
    """
    # Check for X-Forwarded-For header (proxied requests)
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()

    # Check for X-Real-IP header (nginx, etc.)
    if "x-real-ip" in request.headers:
        return request.headers["x-real-ip"]

    # Fall back to direct connection
    return request.client.host if request.client else "0.0.0.0"


async def get_kiosk_from_ip(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Kiosk:
    """Dependency to get kiosk from client IP address.

    Also validates device_fingerprint if provided in headers.

    Args:
        request: FastAPI request object
        session: Database session

    Returns:
        Authenticated Kiosk object

    Raises:
        HTTPException 404: No kiosk found with this IP
        HTTPException 403: Kiosk is not active
        HTTPException 403: Device fingerprint mismatch
    """
    client_ip = get_client_ip(request)

    # Query kiosk by IP address
    result = await session.execute(
        select(Kiosk).where(Kiosk.ip_address == client_ip)
    )
    kiosk = result.scalar_one_or_none()

    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No kiosk registered for IP address: {client_ip}",
        )

    if not kiosk.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kiosk is not active",
        )

    # Optional: validate device fingerprint if provided in header
    device_fingerprint_header = request.headers.get("x-device-fingerprint")
    if device_fingerprint_header:
        if device_fingerprint_header != kiosk.device_fingerprint:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Device fingerprint mismatch",
            )

    return kiosk


async def get_kiosk_from_ip_or_api_key(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Kiosk:
    """Dependency to get kiosk from IP (primary) or API key (fallback).

    This allows for a transition period where both methods work.

    Args:
        request: FastAPI request object
        session: Database session

    Returns:
        Authenticated Kiosk object

    Raises:
        HTTPException 404: No kiosk found with IP or API key
        HTTPException 403: Kiosk is not active
    """
    client_ip = get_client_ip(request)

    # Try IP-based lookup first
    result = await session.execute(
        select(Kiosk).where(Kiosk.ip_address == client_ip)
    )
    kiosk = result.scalar_one_or_none()

    if kiosk:
        if not kiosk.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Kiosk is not active",
            )
        return kiosk

    # Fallback to API key lookup (for backward compatibility)
    from src.routers.kiosk_auth import api_key_header, verify_kiosk_api_key

    api_key = request.headers.get("x-kiosk-api-key")
    if api_key:
        result = await session.execute(
            select(Kiosk).where(Kiosk.api_key_hash.isnot(None))
        )
        kiosks = result.scalars().all()

        for candidate_kiosk in kiosks:
            if verify_kiosk_api_key(api_key, candidate_kiosk.api_key_hash):
                if not candidate_kiosk.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Kiosk is not active",
                    )
                return candidate_kiosk

    # Neither IP nor API key matched
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No kiosk found for IP {client_ip} or API key",
    )
