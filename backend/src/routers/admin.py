from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.dependencies import require_roles
from src.models.audit_log import AuditLog
from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.user import User
from src.routers.kiosk_auth import generate_kiosk_api_key, hash_kiosk_api_key
from src.schemas import (
    AdminUserCreate,
    AuditLogRead,
    DeviceRead,
    HRCodeCreate,
    HRCodeRead,
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


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Delete a user (admin only).

    Args:
        user_id: ID of user to delete

    Returns:
        204 No Content

    Raises:
        HTTPException 404: User not found
        HTTPException 403: Cannot delete yourself
    """
    # Prevent admin from deleting themselves
    if user_id == current.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account",
        )

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found"
        )

    await session.delete(user)
    await session.commit()
    return None


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
    from datetime import datetime

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
        created_at=datetime.utcnow(),
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


class KioskAPIKeyResponse(BaseModel):
    """Response model for kiosk API key generation."""

    kiosk_id: int
    api_key: str
    message: str


@router.post("/kiosks/{kiosk_id}/generate-api-key", response_model=KioskAPIKeyResponse)
async def generate_kiosk_api_key_endpoint(
    kiosk_id: int,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Generate a new API key for a kiosk (admin only).

    This endpoint generates a secure random API key, hashes it, and stores
    the hash in the database. The plain API key is returned ONCE and should
    be securely stored by the kiosk.

    Args:
        kiosk_id: ID of kiosk to generate API key for

    Returns:
        KioskAPIKeyResponse with the plain API key (shown only once)

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

    # Generate new API key
    api_key = generate_kiosk_api_key()
    api_key_hash = hash_kiosk_api_key(api_key)

    # Store hash in database
    kiosk.api_key_hash = api_key_hash
    session.add(kiosk)
    await session.commit()

    return KioskAPIKeyResponse(
        kiosk_id=kiosk_id,
        api_key=api_key,
        message=(
            "API key generated successfully. "
            "Store this key securely - it will not be shown again!"
        ),
    )


@router.delete("/kiosks/{kiosk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kiosk(
    kiosk_id: int,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Delete a kiosk (admin only).

    Args:
        kiosk_id: ID of kiosk to delete

    Returns:
        204 No Content

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

    await session.delete(kiosk)
    await session.commit()
    return None


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


# ==================== Punches ====================


@router.post(
    "/hr-codes", response_model=HRCodeRead, status_code=status.HTTP_201_CREATED
)
async def create_hr_code(
    hr_code_data: HRCodeCreate,
    current_user: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    offset: int = 0,
    limit: int = 50,
):
    """Get punch history with optional filters (admin only).

    Args:
        user_id: Filter by user ID
        from_date: Filter by start date (ISO format)
        to_date: Filter by end date (ISO format)
        offset: Pagination offset
        limit: Maximum results (max 100)

    Returns:
        List of punch records ordered by punched_at descending
    """
    from src.models.punch import Punch
    from src.schemas import PunchRead

    if limit > 100:
        limit = 100

    query = select(Punch)

    if user_id is not None:
        query = query.where(Punch.user_id == user_id)

    if from_date:
        from datetime import datetime

        from_dt = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
        query = query.where(Punch.punched_at >= from_dt)

    if to_date:
        from datetime import datetime

        to_dt = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
        query = query.where(Punch.punched_at <= to_dt)

    result = await session.execute(
        query.order_by(Punch.punched_at.desc()).offset(offset).limit(limit)
    )
    punches = result.scalars().all()

    return [PunchRead.model_validate(punch) for punch in punches]


# ==================== Dashboard Stats ====================


class DashboardStats(BaseModel):
    """Dashboard statistics response model."""

    total_users: int
    total_devices: int
    total_kiosks: int
    active_kiosks: int
    today_punches: int
    today_users: int
    recent_punches: list


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Get dashboard statistics (admin only).

    Returns:
        DashboardStats with current system metrics
    """
    from datetime import datetime, timezone

    from sqlalchemy import func

    from src.models.punch import Punch
    from src.schemas import PunchRead

    # Count total users
    result = await session.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    # Count total devices
    result = await session.execute(select(func.count(Device.id)))
    total_devices = result.scalar() or 0

    # Count total kiosks
    result = await session.execute(select(func.count(Kiosk.id)))
    total_kiosks = result.scalar() or 0

    # Count active kiosks
    result = await session.execute(
        select(func.count(Kiosk.id)).where(Kiosk.is_active.is_(True))
    )
    active_kiosks = result.scalar() or 0

    # Get today's date range
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Count today's punches
    result = await session.execute(
        select(func.count(Punch.id)).where(
            Punch.punched_at >= today_start, Punch.punched_at <= today_end
        )
    )
    today_punches = result.scalar() or 0

    # Count unique users today
    result = await session.execute(
        select(func.count(func.distinct(Punch.user_id))).where(
            Punch.punched_at >= today_start, Punch.punched_at <= today_end
        )
    )
    today_users = result.scalar() or 0

    # Get recent punches (last 10)
    result = await session.execute(
        select(Punch).order_by(Punch.punched_at.desc()).limit(10)
    )
    recent_punches_models = result.scalars().all()
    recent_punches = [
        PunchRead.model_validate(p).model_dump() for p in recent_punches_models
    ]

    return DashboardStats(
        total_users=total_users,
        total_devices=total_devices,
        total_kiosks=total_kiosks,
        active_kiosks=active_kiosks,
        today_punches=today_punches,
        today_users=today_users,
        recent_punches=recent_punches,
    )


# ==================== Reports (Attendance) ====================


@router.get("/reports/attendance")
async def export_attendance_report(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    from_: Annotated[str, Query(alias="from")],  # accept ?from=...
    to: str,  # end date/time
    user_id: Optional[int] = None,
    format: Optional[str] = "json",
):
    """Export attendance records between two dates.

    Query params:
    - from_: ISO date/time or YYYY-MM-DD (inclusive, 00:00)
    - to: ISO date/time or YYYY-MM-DD (inclusive, 23:59:59.999999)
    - user_id: optional filter
    - format: 'json' | 'csv' | 'pdf' (pdf not implemented)
    """
    from datetime import datetime, timezone
    import io
    import csv

    from src.models.punch import Punch
    from src.schemas import PunchRead

    def parse_boundary(value: str, is_start: bool) -> datetime:
        v = value.strip()
        try:
            if len(v) == 10 and v[4] == "-" and v[7] == "-":
                # YYYY-MM-DD
                dt = datetime.fromisoformat(v).replace(tzinfo=timezone.utc)
                if is_start:
                    return dt.replace(hour=0, minute=0, second=0, microsecond=0)
                return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            # Replace trailing Z with +00:00 for fromisoformat
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail="invalid_datetime")

    start_dt = parse_boundary(from_, True)
    end_dt = parse_boundary(to, False)
    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="invalid_range")

    query = select(Punch).where(
        Punch.punched_at >= start_dt, Punch.punched_at <= end_dt
    )
    if user_id is not None:
        query = query.where(Punch.user_id == user_id)

    result = await session.execute(query.order_by(Punch.punched_at.asc()))
    punches = result.scalars().all()

    fmt = (format or "json").lower()
    if fmt == "json":
        data = [PunchRead.model_validate(p).model_dump() for p in punches]
        return JSONResponse(content=jsonable_encoder(data))

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "user_id",
                "device_id",
                "kiosk_id",
                "punch_type",
                "punched_at",
                "jwt_jti",
                "created_at",
            ]
        )
        for p in punches:
            writer.writerow(
                [
                    p.id,
                    p.user_id,
                    p.device_id,
                    p.kiosk_id,
                    (
                        p.punch_type.value
                        if hasattr(p.punch_type, "value")
                        else str(p.punch_type)
                    ),
                    p.punched_at.isoformat(),
                    p.jwt_jti,
                    p.created_at.isoformat(),
                ]
            )
        csv_bytes = output.getvalue().encode("utf-8")
        filename = f"attendance_{start_dt.date()}_{end_dt.date()}.csv"
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    if fmt == "pdf":
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
                Spacer,
            )
        except Exception:
            raise HTTPException(status_code=500, detail="reportlab_not_installed")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, title="Attendance Report")
        styles = getSampleStyleSheet()

        elements = []
        title = Paragraph(
            f"Rapport de présence du {start_dt.date()} au {end_dt.date()}"
            + (f" — Utilisateur #{user_id}" if user_id is not None else ""),
            styles["Title"],
        )
        elements.append(title)
        elements.append(Spacer(1, 12))

        data_rows = [
            [
                "ID",
                "User",
                "Device",
                "Kiosk",
                "Type",
                "Punched At",
            ]
        ]
        for p in punches:
            data_rows.append(
                [
                    str(p.id),
                    str(p.user_id),
                    str(p.device_id),
                    str(p.kiosk_id),
                    (
                        p.punch_type.value
                        if hasattr(p.punch_type, "value")
                        else str(p.punch_type)
                    ),
                    p.punched_at.isoformat(),
                ]
            )

        table = Table(data_rows, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ]
            )
        )
        elements.append(table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        filename = f"attendance_{start_dt.date()}_{end_dt.date()}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    raise HTTPException(status_code=400, detail="invalid_format")
