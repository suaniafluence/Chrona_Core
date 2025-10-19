"""Audit logging service for security events."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog


async def log_event(
    session: AsyncSession,
    event_type: str,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
    kiosk_id: Optional[int] = None,
    event_data: Optional[str] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """Create an audit log entry for a security event.

    Args:
        session: Database session
        event_type: Type of event (e.g., 'device_registered', 'punch_validated')
        user_id: Optional user ID associated with the event
        device_id: Optional device ID associated with the event
        kiosk_id: Optional kiosk ID associated with the event
        event_data: Optional JSON string with additional event details
        request: Optional FastAPI request for IP/user-agent extraction

    Returns:
        Created AuditLog instance
    """
    audit_log = AuditLog(
        event_type=event_type,
        user_id=user_id,
        device_id=device_id,
        kiosk_id=kiosk_id,
        event_data=event_data,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        created_at=datetime.now(timezone.utc),
    )

    session.add(audit_log)
    await session.commit()
    await session.refresh(audit_log)

    return audit_log


async def log_device_registered(
    session: AsyncSession,
    user_id: int,
    device_id: int,
    device_name: str,
    device_fingerprint: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log device registration event.

    Args:
        session: Database session
        user_id: ID of user registering the device
        device_id: ID of newly registered device
        device_name: Human-readable device name
        device_fingerprint: Device fingerprint (truncated for privacy)
        request: Optional FastAPI request

    Returns:
        Created AuditLog instance
    """
    event_data = (
        f'{{"device_name": "{device_name}", '
        f'"device_fingerprint": "{device_fingerprint[:16]}..."}}'
    )

    return await log_event(
        session=session,
        event_type="device_registered",
        user_id=user_id,
        device_id=device_id,
        event_data=event_data,
        request=request,
    )


async def log_device_revoked(
    session: AsyncSession,
    user_id: int,
    device_id: int,
    device_name: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log device revocation event.

    Args:
        session: Database session
        user_id: ID of user revoking the device
        device_id: ID of revoked device
        device_name: Human-readable device name
        request: Optional FastAPI request

    Returns:
        Created AuditLog instance
    """
    event_data = f'{{"device_name": "{device_name}"}}'

    return await log_event(
        session=session,
        event_type="device_revoked",
        user_id=user_id,
        device_id=device_id,
        event_data=event_data,
        request=request,
    )


async def log_punch_validated(
    session: AsyncSession,
    user_id: int,
    device_id: int,
    kiosk_id: int,
    punch_type: str,
    jti: str,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log successful punch validation event.

    Args:
        session: Database session
        user_id: ID of user who punched
        device_id: ID of device used for punch
        kiosk_id: ID of kiosk that validated the punch
        punch_type: Type of punch ('clock_in' or 'clock_out')
        jti: JWT token ID
        request: Optional FastAPI request

    Returns:
        Created AuditLog instance
    """
    event_data = f'{{"punch_type": "{punch_type}", "jti": "{jti}"}}'

    return await log_event(
        session=session,
        event_type="punch_validated",
        user_id=user_id,
        device_id=device_id,
        kiosk_id=kiosk_id,
        event_data=event_data,
        request=request,
    )


async def log_replay_attempt(
    session: AsyncSession,
    user_id: int,
    device_id: int,
    kiosk_id: int,
    jti: str,
    nonce: str,
    first_consumed_at: datetime,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log token replay attack attempt.

    Args:
        session: Database session
        user_id: ID of user associated with the token
        device_id: ID of device associated with the token
        kiosk_id: ID of kiosk attempting to reuse the token
        jti: JWT token ID
        nonce: Token nonce value
        first_consumed_at: Timestamp when token was first consumed
        request: Optional FastAPI request

    Returns:
        Created AuditLog instance
    """
    event_data = (
        f'{{"jti": "{jti}", "nonce": "{nonce}", '
        f'"first_consumed_at": "{first_consumed_at}"}}'
    )

    return await log_event(
        session=session,
        event_type="punch_replay_attempt",
        user_id=user_id,
        device_id=device_id,
        kiosk_id=kiosk_id,
        event_data=event_data,
        request=request,
    )
