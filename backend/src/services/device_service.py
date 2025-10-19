"""Device management service."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.device import Device
from src.services import audit_service


async def register_device(
    session: AsyncSession,
    user_id: int,
    device_fingerprint: str,
    device_name: str,
    attestation_data: Optional[str] = None,
    request: Optional[Request] = None,
) -> Device:
    """Register a new device for a user.

    Args:
        session: Database session
        user_id: ID of user registering the device
        device_fingerprint: Unique device identifier (hashed)
        device_name: Human-readable device name
        attestation_data: Optional SafetyNet/DeviceCheck attestation JSON
        request: Optional FastAPI request for audit logging

    Returns:
        Created Device instance

    Raises:
        HTTPException 409: Device fingerprint already registered for this user
    """
    # Check if device already exists for this user
    result = await session.execute(
        select(Device).where(
            Device.user_id == user_id,
            Device.device_fingerprint == device_fingerprint,
        )
    )
    existing_device = result.scalar_one_or_none()

    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device with this fingerprint already registered for user",
        )

    # Create new device
    now = datetime.now(timezone.utc)
    device = Device(
        user_id=user_id,
        device_fingerprint=device_fingerprint,
        device_name=device_name,
        attestation_data=attestation_data,
        registered_at=now,
        last_seen_at=now,
        is_revoked=False,
    )
    session.add(device)
    await session.commit()
    await session.refresh(device)

    # Create audit log
    await audit_service.log_device_registered(
        session=session,
        user_id=user_id,
        device_id=device.id,
        device_name=device_name,
        device_fingerprint=device_fingerprint,
        request=request,
    )

    return device


async def revoke_device(
    session: AsyncSession,
    device_id: int,
    revoked_by_user_id: int,
    request: Optional[Request] = None,
) -> Device:
    """Revoke a device.

    Args:
        session: Database session
        device_id: ID of device to revoke
        revoked_by_user_id: ID of user revoking the device
        request: Optional FastAPI request for audit logging

    Returns:
        Updated Device instance

    Raises:
        HTTPException 404: Device not found
        HTTPException 400: Device already revoked
    """
    # Fetch device
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    if device.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device is already revoked",
        )

    # Revoke device
    device.is_revoked = True
    session.add(device)
    await session.commit()
    await session.refresh(device)

    # Create audit log
    await audit_service.log_device_revoked(
        session=session,
        user_id=revoked_by_user_id,
        device_id=device.id,
        device_name=device.device_name,
        request=request,
    )

    return device


async def get_user_devices(
    session: AsyncSession,
    user_id: int,
    include_revoked: bool = False,
) -> list[Device]:
    """Get all devices for a user.

    Args:
        session: Database session
        user_id: ID of user
        include_revoked: Whether to include revoked devices (default False)

    Returns:
        List of Device instances ordered by registered_at descending
    """
    query = select(Device).where(Device.user_id == user_id)

    if not include_revoked:
        query = query.where(Device.is_revoked.is_(False))

    result = await session.execute(query.order_by(Device.registered_at.desc()))
    devices = result.scalars().all()

    return list(devices)
