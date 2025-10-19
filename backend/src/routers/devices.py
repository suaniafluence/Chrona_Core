"""Device management endpoints for employee device registration and revocation."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models import User
from src.models.audit_log import AuditLog
from src.models.device import Device
from src.routers.auth import get_current_user
from src.schemas import DeviceCreate, DeviceRead

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post(
    "/register", response_model=DeviceRead, status_code=status.HTTP_201_CREATED
)
async def register_device(
    device_data: DeviceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> DeviceRead:
    """Register a new device for the authenticated user.

    Args:
        device_data: Device registration data (fingerprint, name, attestation)
        current_user: Authenticated user (from JWT)
        db: Database session
        request: FastAPI request (for IP/user-agent logging)

    Returns:
        DeviceRead with created device information

    Raises:
        HTTPException 409: Device fingerprint already registered
    """
    # Check if device_fingerprint already exists for this user
    result = await session.execute(
        select(Device).where(
            Device.user_id == current_user.id,
            Device.device_fingerprint == device_data.device_fingerprint,
        )
    )
    existing_device = result.scalar_one_or_none()

    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device with this fingerprint already registered for user",
        )

    # Create new device
    # Use naive UTC to match TIMESTAMP WITHOUT TIME ZONE columns
    now = datetime.utcnow()
    device = Device(
        user_id=current_user.id,
        device_fingerprint=device_data.device_fingerprint,
        device_name=device_data.device_name,
        attestation_data=device_data.attestation_data,
        registered_at=now,
        last_seen_at=now,
        is_revoked=False,
    )
    session.add(device)

    # Create audit log
    audit_log = AuditLog(
        event_type="device_registered",
        user_id=current_user.id,
        device_id=None,  # Will be set after commit
        event_data=(
            f'{{"device_name": "{device_data.device_name}", '
            f'"device_fingerprint": "{device_data.device_fingerprint[:16]}..."}}'
        ),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(device)

    # Update audit log with device_id
    audit_log.device_id = device.id
    session.add(audit_log)
    await session.commit()

    return DeviceRead.model_validate(device)


@router.get("/me", response_model=list[DeviceRead])
async def list_my_devices(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    include_revoked: bool = False,
) -> list[DeviceRead]:
    """List all devices registered for the authenticated user.

    Args:
        current_user: Authenticated user (from JWT)
        session: Database session
        include_revoked: Whether to include revoked devices (default False)

    Returns:
        List of DeviceRead records ordered by registered_at descending
    """
    query = select(Device).where(Device.user_id == current_user.id)

    if not include_revoked:
        query = query.where(Device.is_revoked.is_(False))

    result = await session.execute(query.order_by(Device.registered_at.desc()))
    devices = result.scalars().all()

    return [DeviceRead.model_validate(device) for device in devices]


@router.post("/{device_id}/revoke", response_model=DeviceRead)
async def revoke_device(
    device_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> DeviceRead:
    """Revoke a device (only owner can revoke their own devices).

    Args:
        device_id: ID of device to revoke
        current_user: Authenticated user (from JWT)
        session: Database session
        request: FastAPI request (for IP/user-agent logging)

    Returns:
        DeviceRead with updated device information

    Raises:
        HTTPException 404: Device not found or not owned by user
        HTTPException 400: Device already revoked
    """
    # Verify device exists and belongs to current user
    result = await session.execute(
        select(Device).where(Device.id == device_id, Device.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by user",
        )

    if device.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device is already revoked",
        )

    # Revoke device
    device.is_revoked = True
    session.add(device)

    # Create audit log
    audit_log = AuditLog(
        event_type="device_revoked",
        user_id=current_user.id,
        device_id=device.id,
        event_data=f'{{"device_name": "{device.device_name}"}}',
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(device)

    return DeviceRead.model_validate(device)
