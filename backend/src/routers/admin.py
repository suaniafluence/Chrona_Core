from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models.audit_log import AuditLog
from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.user import User
from src.routers.auth import require_roles
from src.schemas import (
    AdminUserCreate,
    AuditLogRead,
    DeviceRead,
    KioskCreate,
    KioskRead,
    KioskUpdate,
    UserRead,
)
from src.security import get_password_hash
from src.services import device_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
async def ping_admin(_current: Annotated[User, Depends(require_roles("admin"))]):
    return {"pong": True}


class SetRoleRequest(BaseModel):
    role: str


@router.api_route(
    "/users/{user_id}/role", methods=["PATCH", "POST"], response_model=UserRead
)
async def set_user_role(
    user_id: int,
    payload: SetRoleRequest,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    allowed = {"admin", "user", "manager"}
    role = payload.role.strip().lower()
    if role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_role"
        )

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found"
        )

    user.role = role
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


@router.get("/users", response_model=list[UserRead])
async def list_users(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: int = 0,
    limit: int = 50,
):
    if limit > 100:
        limit = 100
    result = await session.execute(select(User).offset(offset).limit(limit))
    users = result.scalars().all()
    return [UserRead.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found"
        )
    return UserRead.model_validate(user)


@router.post("/users", response_model=UserRead, status_code=201)
async def create_user_with_role(
    payload: AdminUserCreate,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    allowed = {"admin", "user", "manager"}
    role = payload.role.strip().lower()
    if role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_role"
        )
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=role,
    )
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email_already_registered"
        )
    return UserRead.model_validate(user)


# ==================== Device Management ====================


@router.get("/devices", response_model=list[DeviceRead])
async def list_all_devices(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Optional[int] = None,
    is_revoked: Optional[bool] = None,
    offset: int = 0,
    limit: int = 50,
):
    """List all devices with optional filters (admin only).

    Args:
        user_id: Filter by user ID
        is_revoked: Filter by revocation status
        offset: Pagination offset
        limit: Maximum results (max 100)

    Returns:
        List of DeviceRead
    """
    if limit > 100:
        limit = 100

    query = select(Device)

    if user_id is not None:
        query = query.where(Device.user_id == user_id)

    if is_revoked is not None:
        query = query.where(Device.is_revoked == is_revoked)

    result = await session.execute(
        query.order_by(Device.registered_at.desc()).offset(offset).limit(limit)
    )
    devices = result.scalars().all()

    return [DeviceRead.model_validate(device) for device in devices]


@router.post("/devices/{device_id}/revoke", response_model=DeviceRead)
async def admin_revoke_device(
    device_id: int,
    current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
):
    """Revoke any device (admin only).

    Args:
        device_id: ID of device to revoke

    Returns:
        Updated DeviceRead
    """
    device = await device_service.revoke_device(
        session=session,
        device_id=device_id,
        revoked_by_user_id=current.id,
        request=request,
    )

    return DeviceRead.model_validate(device)


# ==================== Kiosk Management ====================


@router.get("/kiosks", response_model=list[KioskRead])
async def list_kiosks(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    is_active: Optional[bool] = None,
    offset: int = 0,
    limit: int = 50,
):
    """List all kiosks with optional filters (admin only).

    Args:
        is_active: Filter by active status
        offset: Pagination offset
        limit: Maximum results (max 100)

    Returns:
        List of KioskRead
    """
    if limit > 100:
        limit = 100

    query = select(Kiosk)

    if is_active is not None:
        query = query.where(Kiosk.is_active == is_active)

    result = await session.execute(
        query.order_by(Kiosk.created_at.desc()).offset(offset).limit(limit)
    )
    kiosks = result.scalars().all()

    return [KioskRead.model_validate(kiosk) for kiosk in kiosks]


@router.post("/kiosks", response_model=KioskRead, status_code=status.HTTP_201_CREATED)
async def create_kiosk(
    kiosk_data: KioskCreate,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Create a new kiosk (admin only).

    Args:
        kiosk_data: Kiosk creation data

    Returns:
        Created KioskRead

    Raises:
        HTTPException 409: Kiosk name or fingerprint already exists
    """
    from datetime import datetime, timezone

    # Check for duplicate kiosk_name
    result = await session.execute(
        select(Kiosk).where(Kiosk.kiosk_name == kiosk_data.kiosk_name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kiosk with this name already exists",
        )

    # Check for duplicate device_fingerprint
    result = await session.execute(
        select(Kiosk).where(Kiosk.device_fingerprint == kiosk_data.device_fingerprint)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kiosk with this fingerprint already exists",
        )

    # Create kiosk
    kiosk = Kiosk(
        kiosk_name=kiosk_data.kiosk_name,
        location=kiosk_data.location,
        device_fingerprint=kiosk_data.device_fingerprint,
        public_key=kiosk_data.public_key,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    session.add(kiosk)
    await session.commit()
    await session.refresh(kiosk)

    return KioskRead.model_validate(kiosk)


@router.patch("/kiosks/{kiosk_id}", response_model=KioskRead)
async def update_kiosk(
    kiosk_id: int,
    kiosk_data: KioskUpdate,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Update a kiosk (admin only).

    Args:
        kiosk_id: ID of kiosk to update
        kiosk_data: Fields to update

    Returns:
        Updated KioskRead

    Raises:
        HTTPException 404: Kiosk not found
    """
    result = await session.execute(select(Kiosk).where(Kiosk.id == kiosk_id))
    kiosk = result.scalar_one_or_none()

    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kiosk not found",
        )

    # Update fields if provided
    if kiosk_data.kiosk_name is not None:
        kiosk.kiosk_name = kiosk_data.kiosk_name

    if kiosk_data.location is not None:
        kiosk.location = kiosk_data.location

    if kiosk_data.is_active is not None:
        kiosk.is_active = kiosk_data.is_active

    session.add(kiosk)
    await session.commit()
    await session.refresh(kiosk)

    return KioskRead.model_validate(kiosk)


# ==================== Audit Logs ====================


@router.get("/audit-logs", response_model=list[AuditLogRead])
async def get_audit_logs(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
    kiosk_id: Optional[int] = None,
    offset: int = 0,
    limit: int = 50,
):
    """Get audit logs with optional filters (admin only).

    Args:
        event_type: Filter by event type
        user_id: Filter by user ID
        device_id: Filter by device ID
        kiosk_id: Filter by kiosk ID
        offset: Pagination offset
        limit: Maximum results (max 100)

    Returns:
        List of AuditLogRead ordered by created_at descending
    """
    if limit > 100:
        limit = 100

    query = select(AuditLog)

    if event_type:
        query = query.where(AuditLog.event_type == event_type)

    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)

    if device_id is not None:
        query = query.where(AuditLog.device_id == device_id)

    if kiosk_id is not None:
        query = query.where(AuditLog.kiosk_id == kiosk_id)

    result = await session.execute(
        query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    )
    logs = result.scalars().all()

    return [AuditLogRead.model_validate(log) for log in logs]
