"""Onboarding endpoints for Level B employee registration."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.models import User
from src.models.audit_log import AuditLog
from src.models.device import Device
from src.routers.auth import create_access_token
from src.schemas import (
    OnboardingCompleteRequest,
    OnboardingCompleteResponse,
    OnboardingInitiateRequest,
    OnboardingInitiateResponse,
    OnboardingVerifyOTPRequest,
    OnboardingVerifyOTPResponse,
)
from src.security import get_password_hash
from src.services.hr_code_service import HRCodeService
from src.services.onboarding_service import OnboardingService
from src.services.otp_service import OTPService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post("/initiate", response_model=OnboardingInitiateResponse)
async def initiate_onboarding(
    request_data: OnboardingInitiateRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> OnboardingInitiateResponse:
    """Initiate Level B onboarding with HR code verification.

    Step 1: Validate HR code and create onboarding session.

    Args:
        request_data: HR code and email
        session: Database session
        request: FastAPI request

    Returns:
        OnboardingInitiateResponse with session token
    """
    # Validate HR code
    is_valid, hr_code, error_msg = await HRCodeService.validate_hr_code(
        session, request_data.hr_code, request_data.email
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or "Code HR invalide",
        )

    # Create onboarding session
    onboarding_session = await OnboardingService.create_session(
        session=session,
        email=request_data.email,
        hr_code_id=hr_code.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Generate and send OTP
    otp_record, otp_code = await OTPService.create_otp(
        session=session,
        email=request_data.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Send OTP via email
    await OTPService.send_otp_email(request_data.email, otp_code)

    # Update session step
    await OnboardingService.update_session_step(session, onboarding_session, "otp_sent")

    # Create audit log
    audit_log = AuditLog(
        event_type="onboarding_initiated",
        user_id=None,
        event_data=(
            f'{{"email": "{request_data.email}", '
            f'"hr_code": "{request_data.hr_code}"}}'
        ),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    session.add(audit_log)
    await session.commit()

    return OnboardingInitiateResponse(
        success=True,
        message="Code OTP envoyé par email",
        session_token=onboarding_session.session_token,
        step="otp_sent",
    )


@router.post("/verify-otp", response_model=OnboardingVerifyOTPResponse)
async def verify_otp(
    request_data: OnboardingVerifyOTPRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> OnboardingVerifyOTPResponse:
    """Verify OTP code during onboarding.

    Step 2: Validate OTP and advance onboarding session.

    Args:
        request_data: Session token and OTP code
        session: Database session
        request: FastAPI request

    Returns:
        OnboardingVerifyOTPResponse with next step
    """
    # Validate onboarding session
    is_valid, onboarding_session, error_msg = await OnboardingService.validate_session(
        session, request_data.session_token
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or "Session invalide",
        )

    # Verify OTP
    is_otp_valid, otp_record, otp_error = await OTPService.verify_otp(
        session, onboarding_session.email, request_data.otp_code
    )

    if not is_otp_valid:
        # Create audit log for failed attempt
        audit_log = AuditLog(
            event_type="onboarding_otp_failed",
            user_id=None,
            event_data=f'{{"email": "{onboarding_session.email}"}}',
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        session.add(audit_log)
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=otp_error or "Code OTP invalide",
        )

    # Update session step
    await OnboardingService.update_session_step(
        session, onboarding_session, "otp_verified"
    )

    # Create audit log
    audit_log = AuditLog(
        event_type="onboarding_otp_verified",
        user_id=None,
        event_data=f'{{"email": "{onboarding_session.email}"}}',
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    session.add(audit_log)
    await session.commit()

    return OnboardingVerifyOTPResponse(
        success=True,
        message="Code OTP vérifié avec succès",
        step="device_attestation",
    )


@router.post("/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(
    request_data: OnboardingCompleteRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> OnboardingCompleteResponse:
    """Complete onboarding with device attestation and account creation.

    Step 3: Validate device attestation, create user account, register device.

    Args:
        request_data: Session token, password, device info, attestation
        session: Database session
        request: FastAPI request

    Returns:
        OnboardingCompleteResponse with user/device IDs and access token
    """
    # Validate onboarding session
    is_valid, onboarding_session, error_msg = await OnboardingService.validate_session(
        session, request_data.session_token
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or "Session invalide",
        )

    # Check session step
    if onboarding_session.step != "otp_verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez d'abord vérifier le code OTP",
        )

    # Validate device attestation (placeholder - implement SafetyNet/DeviceCheck validation)
    # TODO: Implement actual attestation validation
    if request_data.attestation_data:
        # Validate SafetyNet (Android) or DeviceCheck (iOS) attestation
        # For now, we accept any attestation data
        pass

    # Create user account
    hashed_password = get_password_hash(request_data.password)
    now = datetime.now(timezone.utc)

    user = User(
        email=onboarding_session.email,
        hashed_password=hashed_password,
        role="user",
        created_at=now,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Register device
    device = Device(
        user_id=user.id,
        device_fingerprint=request_data.device_fingerprint,
        device_name=request_data.device_name,
        attestation_data=request_data.attestation_data,
        registered_at=now,
        last_seen_at=now,
        is_revoked=False,
    )
    session.add(device)
    await session.commit()
    await session.refresh(device)

    # Mark HR code as used
    if onboarding_session.hr_code_id:
        from sqlmodel import select

        from src.models.hr_code import HRCode

        result = await session.execute(
            select(HRCode).where(HRCode.id == onboarding_session.hr_code_id)
        )
        hr_code = result.scalar_one_or_none()
        if hr_code:
            await HRCodeService.mark_hr_code_used(session, hr_code, user.id)

    # Complete onboarding session
    await OnboardingService.complete_session(session, onboarding_session)

    # Create audit log
    audit_log = AuditLog(
        event_type="onboarding_completed",
        user_id=user.id,
        device_id=device.id,
        event_data=(
            f'{{"email": "{user.email}", ' f'"device_name": "{device.device_name}"}}'
        ),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    session.add(audit_log)
    await session.commit()

    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return OnboardingCompleteResponse(
        success=True,
        message="Onboarding terminé avec succès",
        user_id=user.id,
        device_id=device.id,
        access_token=access_token,
    )
