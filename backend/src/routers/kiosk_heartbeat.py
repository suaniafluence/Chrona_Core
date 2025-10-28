"""Kiosk heartbeat/ping endpoints for monitoring."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..db import get_session
from ..models.kiosk import Kiosk
from ..routers.kiosk_auth import get_current_kiosk

router = APIRouter(prefix="/kiosk", tags=["kiosk-heartbeat"])


class HeartbeatRequest(BaseModel):
    """Request body for kiosk heartbeat."""

    app_version: str = Field(..., max_length=50, description="Mobile app version")
    device_info: str | None = Field(
        None, max_length=255, description="Device model and OS info"
    )


class HeartbeatResponse(BaseModel):
    """Response for heartbeat ping."""

    success: bool
    message: str
    kiosk_id: int
    last_heartbeat_at: datetime
    server_time: datetime


class KioskStatusResponse(BaseModel):
    """Kiosk status information."""

    kiosk_id: int
    kiosk_name: str
    location: str
    is_active: bool
    last_heartbeat_at: datetime | None
    app_version: str | None
    device_info: str | None
    is_online: bool
    offline_duration_seconds: int | None


@router.post("/heartbeat", response_model=HeartbeatResponse)
async def send_heartbeat(
    heartbeat: HeartbeatRequest,
    kiosk: Annotated[Kiosk, Depends(get_current_kiosk)],
    session: Annotated[Session, Depends(get_session)],
):
    """
    Record a heartbeat/ping from a kiosk tablet.

    This endpoint should be called periodically (e.g., every 30-60 seconds)
    by the kiosk app to signal that it's online and functioning.

    Returns the updated heartbeat timestamp.
    """
    # Update kiosk heartbeat fields
    kiosk.last_heartbeat_at = datetime.utcnow()
    kiosk.app_version = heartbeat.app_version
    if heartbeat.device_info:
        kiosk.device_info = heartbeat.device_info

    session.add(kiosk)
    session.commit()
    session.refresh(kiosk)

    return HeartbeatResponse(
        success=True,
        message="Heartbeat recorded successfully",
        kiosk_id=kiosk.id,
        last_heartbeat_at=kiosk.last_heartbeat_at,
        server_time=datetime.utcnow(),
    )


@router.get("/status", response_model=KioskStatusResponse)
async def get_kiosk_status(
    kiosk: Annotated[Kiosk, Depends(get_current_kiosk)],
):
    """
    Get the current status of the authenticated kiosk.

    Returns heartbeat information and online/offline status.
    """
    now = datetime.utcnow()
    is_online = False
    offline_duration_seconds = None

    if kiosk.last_heartbeat_at:
        # Consider online if heartbeat within last 5 minutes (300 seconds)
        time_since_heartbeat = (now - kiosk.last_heartbeat_at).total_seconds()
        is_online = time_since_heartbeat < 300  # 5 minutes
        if not is_online:
            offline_duration_seconds = int(time_since_heartbeat)

    return KioskStatusResponse(
        kiosk_id=kiosk.id,
        kiosk_name=kiosk.kiosk_name,
        location=kiosk.location,
        is_active=kiosk.is_active,
        last_heartbeat_at=kiosk.last_heartbeat_at,
        app_version=kiosk.app_version,
        device_info=kiosk.device_info,
        is_online=is_online,
        offline_duration_seconds=offline_duration_seconds,
    )


@router.get("/all-status", response_model=list[KioskStatusResponse])
async def get_all_kiosks_status(
    session: Annotated[Session, Depends(get_session)],
    # TODO: Add admin authentication dependency
):
    """
    Get the status of all kiosks (admin only).

    Returns heartbeat information and online/offline status for all registered kiosks.
    Useful for monitoring dashboard in back-office.
    """
    statement = select(Kiosk).order_by(Kiosk.kiosk_name)
    kiosks = session.execute(statement).all()

    now = datetime.utcnow()
    results = []

    for kiosk in kiosks:
        is_online = False
        offline_duration_seconds = None

        if kiosk.last_heartbeat_at:
            time_since_heartbeat = (now - kiosk.last_heartbeat_at).total_seconds()
            is_online = time_since_heartbeat < 300  # 5 minutes
            if not is_online:
                offline_duration_seconds = int(time_since_heartbeat)

        results.append(
            KioskStatusResponse(
                kiosk_id=kiosk.id,
                kiosk_name=kiosk.kiosk_name,
                location=kiosk.location,
                is_active=kiosk.is_active,
                last_heartbeat_at=kiosk.last_heartbeat_at,
                app_version=kiosk.app_version,
                device_info=kiosk.device_info,
                is_online=is_online,
                offline_duration_seconds=offline_duration_seconds,
            )
        )

    return results
