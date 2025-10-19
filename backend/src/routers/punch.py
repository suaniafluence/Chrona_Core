"""Punch endpoints for time tracking (QR token generation and validation)."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models import User
from src.models.audit_log import AuditLog
from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.punch import Punch
from src.models.token_tracking import TokenTracking
from src.routers.auth import get_current_user
from src.routers.kiosk_auth import get_current_kiosk
from src.schemas import (
    PunchRead,
    PunchValidateRequest,
    PunchValidateResponse,
    QRTokenRequest,
    QRTokenResponse,
)
from src.security import create_ephemeral_qr_token, decode_token

router = APIRouter(prefix="/punch", tags=["Punch"])


@router.post("/request-token", response_model=QRTokenResponse)
async def request_qr_token(
    request_data: QRTokenRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QRTokenResponse:
    """Generate an ephemeral JWT token for QR code display.

    The mobile app calls this endpoint to get a JWT token that it will
    encode into a QR code. The token is short-lived (30s) and contains
    nonce/jti for replay protection.

    Args:
        request_data: Contains device_id
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        QRTokenResponse with qr_token, expires_in, expires_at

    Raises:
        HTTPException 404: Device not found or not owned by user
        HTTPException 403: Device is revoked
    """
    # Verify device exists and belongs to current user
    result = await session.execute(
        select(Device).where(
            Device.id == request_data.device_id,
            Device.user_id == current_user.id,
        )
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or not owned by user",
        )

    if device.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device has been revoked",
        )

    # Generate ephemeral JWT token
    qr_token, payload = create_ephemeral_qr_token(
        user_id=current_user.id, device_id=device.id
    )

    # Store token tracking record for single-use enforcement
    token_tracking = TokenTracking(
        jti=payload["jti"],
        nonce=payload["nonce"],
        user_id=current_user.id,
        device_id=device.id,
        issued_at=payload["iat"],
        expires_at=payload["exp"],
        consumed_at=None,
        consumed_by_kiosk_id=None,
    )
    session.add(token_tracking)

    # Update device last_seen_at
    device.last_seen_at = datetime.now(timezone.utc)
    session.add(device)

    await session.commit()

    return QRTokenResponse(
        qr_token=qr_token,
        expires_in=int((payload["exp"] - payload["iat"]).total_seconds()),
        expires_at=payload["exp"],
    )


@router.post("/validate", response_model=PunchValidateResponse)
async def validate_punch(
    validate_data: PunchValidateRequest,
    current_kiosk: Annotated[Kiosk, Depends(get_current_kiosk)],
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> PunchValidateResponse:
    """Validate a QR code and record a punch event.

    The kiosk calls this endpoint after scanning a QR code. This endpoint
    performs all security validations (signature, expiration, nonce, jti,
    device, kiosk) and atomically records the punch.

    Args:
        validate_data: Contains qr_token, kiosk_id, punch_type
        db: Database session
        request: FastAPI request (for IP/user-agent logging)

    Returns:
        PunchValidateResponse with success status and punch details

    Raises:
        HTTPException 400: Invalid token, expired, or already used
        HTTPException 403: Device revoked or kiosk not active
        HTTPException 404: Device, kiosk, or user not found
    """

    # 1. Decode and verify JWT signature
    payload = decode_token(validate_data.qr_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or malformed JWT token",
        )

    # 2. Verify token type
    if payload.get("type") != "ephemeral_qr":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type (not an ephemeral QR token)",
        )

    # 3. Verify expiration (decode_token already checks this via jose)
    # Additional explicit check for clarity
    exp = payload.get("exp")
    if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired",
        )

    # 4. Extract payload fields
    user_id = int(payload.get("sub", 0))
    device_id = payload.get("device_id")
    nonce = payload.get("nonce")
    jti = payload.get("jti")

    if not all([user_id, device_id, nonce, jti]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token missing required fields (sub, device_id, nonce, jti)",
        )

    # 5. Verify nonce/jti not already consumed (atomic check + mark)
    result = await session.execute(
        select(TokenTracking).where(TokenTracking.jti == jti)
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token not found in tracking database (may be forged)",
        )

    if token_record.consumed_at is not None:
        # Log replay attempt
        audit_log = AuditLog(
            event_type="punch_replay_attempt",
            user_id=user_id,
            device_id=device_id,
            kiosk_id=validate_data.kiosk_id,
            event_data=(
                f'{{"jti": "{jti}", "nonce": "{nonce}", '
                f'"first_consumed_at": "{token_record.consumed_at}"}}'
            ),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        session.add(audit_log)
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has already been used (replay attack detected)",
        )

    # 6. Verify device exists and is not revoked
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    if device.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device has been revoked",
        )

    # 7. Verify kiosk_id matches authenticated kiosk
    # The current_kiosk is already authenticated and verified as active
    if validate_data.kiosk_id != current_kiosk.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kiosk ID in request does not match authenticated kiosk",
        )

    kiosk = current_kiosk

    # 8. Verify user exists
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 9. Atomically mark token as consumed and create punch record
    now = datetime.now(timezone.utc)
    token_record.consumed_at = now
    token_record.consumed_by_kiosk_id = kiosk.id
    session.add(token_record)

    punch = Punch(
        user_id=user_id,
        device_id=device_id,
        kiosk_id=kiosk.id,
        punch_type=validate_data.punch_type,
        punched_at=now,
        jwt_jti=jti,
    )
    session.add(punch)

    # 10. Create audit log
    audit_log = AuditLog(
        event_type="punch_validated",
        user_id=user_id,
        device_id=device_id,
        kiosk_id=kiosk.id,
        event_data=(
            f'{{"punch_type": "{validate_data.punch_type.value}", ' f'"jti": "{jti}"}}'
        ),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(punch)

    return PunchValidateResponse(
        success=True,
        message=f"Punch {validate_data.punch_type.value} recorded successfully",
        punch_id=punch.id,
        punched_at=punch.punched_at,
        user_id=user_id,
        device_id=device_id,
    )


@router.get("/history", response_model=list[PunchRead])
async def get_punch_history(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = 50,
    offset: int = 0,
) -> list[PunchRead]:
    """Get punch history for the authenticated user.

    Args:
        current_user: Authenticated user (from JWT)
        session: Database session
        limit: Maximum number of records to return (default 50, max 100)
        offset: Number of records to skip (for pagination)

    Returns:
        List of PunchRead records ordered by punched_at descending
    """
    # Limit the maximum limit to prevent abuse
    limit = min(limit, 100)

    result = await session.execute(
        select(Punch)
        .where(Punch.user_id == current_user.id)
        .order_by(Punch.punched_at.desc())
        .limit(limit)
        .offset(offset)
    )
    punches = result.scalars().all()

    return [PunchRead.model_validate(punch) for punch in punches]
