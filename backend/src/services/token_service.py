"""Token service for ephemeral QR token generation and validation."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.device import Device
from src.models.kiosk import Kiosk
from src.models.punch import Punch, PunchType
from src.models.token_tracking import TokenTracking
from src.models.user import User
from src.schemas import QRTokenResponse
from src.security import create_ephemeral_qr_token, decode_token
from src.services import audit_service


async def generate_ephemeral_token(
    session: AsyncSession,
    user_id: int,
    device_id: int,
) -> QRTokenResponse:
    """Generate an ephemeral JWT token for QR code display.

    Args:
        session: Database session
        user_id: ID of user requesting the token
        device_id: ID of device making the request

    Returns:
        QRTokenResponse with token, expires_in, and expires_at

    Raises:
        HTTPException 404: Device not found or not owned by user
        HTTPException 403: Device has been revoked
    """
    # Verify device exists and belongs to user
    result = await session.execute(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == user_id,
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
        user_id=user_id, device_id=device.id
    )

    # Store token tracking record for single-use enforcement
    token_tracking = TokenTracking(
        jti=payload["jti"],
        nonce=payload["nonce"],
        user_id=user_id,
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


async def validate_token_and_punch(
    session: AsyncSession,
    qr_token: str,
    kiosk_id: int,
    punch_type: PunchType,
    request: Optional[Request] = None,
) -> Punch:
    """Validate a QR token and create a punch record.

    This function performs all security validations:
    1. Decode and verify JWT signature
    2. Verify token type is 'ephemeral_qr'
    3. Verify token has not expired
    4. Verify token has not been used (jti single-use)
    5. Verify device exists and is not revoked
    6. Verify kiosk exists and is active
    7. Verify user exists
    8. Atomically mark token as consumed and create punch

    Args:
        session: Database session
        qr_token: JWT token from QR code
        kiosk_id: ID of kiosk scanning the QR
        punch_type: Type of punch (clock_in or clock_out)
        request: Optional FastAPI request for audit logging

    Returns:
        Created Punch instance

    Raises:
        HTTPException 400: Invalid token, expired, or already used
        HTTPException 403: Device revoked or kiosk not active
        HTTPException 404: Device, kiosk, or user not found
    """
    # 1. Decode and verify JWT signature
    payload = decode_token(qr_token)
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

    # 3. Verify expiration
    exp = payload.get("exp")
    if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired",
        )

    # Extract payload fields
    user_id = int(payload.get("sub", 0))
    device_id = payload.get("device_id")
    nonce = payload.get("nonce")
    jti = payload.get("jti")

    if not all([user_id, device_id, nonce, jti]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token missing required fields (sub, device_id, nonce, jti)",
        )

    # 4. Verify nonce/jti not already consumed
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
        await audit_service.log_replay_attempt(
            session=session,
            user_id=user_id,
            device_id=device_id,
            kiosk_id=kiosk_id,
            jti=jti,
            nonce=nonce,
            first_consumed_at=token_record.consumed_at,
            request=request,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has already been used (replay attack detected)",
        )

    # 5. Verify device exists and is not revoked
    result = await session.execute(
        select(Device).where(Device.id == device_id)
    )
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

    # 6. Verify kiosk exists and is active
    result = await session.execute(
        select(Kiosk).where(Kiosk.id == kiosk_id)
    )
    kiosk = result.scalar_one_or_none()

    if not kiosk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kiosk not found",
        )

    if not kiosk.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kiosk is not active",
        )

    # 7. Verify user exists
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 8. Atomically mark token as consumed and create punch
    now = datetime.now(timezone.utc)
    token_record.consumed_at = now
    token_record.consumed_by_kiosk_id = kiosk.id
    session.add(token_record)

    punch = Punch(
        user_id=user_id,
        device_id=device_id,
        kiosk_id=kiosk.id,
        punch_type=punch_type,
        punched_at=now,
        jwt_jti=jti,
    )
    session.add(punch)

    # Create audit log
    await audit_service.log_punch_validated(
        session=session,
        user_id=user_id,
        device_id=device_id,
        kiosk_id=kiosk.id,
        punch_type=punch_type.value,
        jti=jti,
        request=request,
    )

    await session.commit()
    await session.refresh(punch)

    return punch
