"""TOTP (Time-based One-Time Password) authentication endpoints.

Implements secure TOTP API compliant with:
- Employee security spec (provisioning, activation, validation)
- Kiosk security spec (rate limiting, lockout, replay protection)
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from src.db import get_session
from src.dependencies import get_current_user
from src.models import TOTPSecret, User
from src.totp import (
    activate_totp,
    initiate_totp_provisioning,
)
from src.totp.encryption import decrypt_secret
from src.totp.provisioning import validate_totp_code
from src.totp.recovery import (
    create_recovery_codes,
    get_recovery_codes_status,
    regenerate_recovery_codes,
    use_recovery_code,
)
from src.totp.security import (
    AccountLocked,
    RateLimitExceeded,
    blacklist_nonce,
    check_account_lockout,
    check_rate_limit,
    get_failed_attempts_count,
    is_nonce_blacklisted,
    record_validation_attempt,
    should_trigger_alert,
    trigger_lockout,
)

router = APIRouter(prefix="/totp", tags=["totp"])


# --- Request/Response Schemas ---


class TOTPProvisionRequest(BaseModel):
    """Request to initiate TOTP provisioning."""

    device_id: Optional[int] = Field(
        default=None, description="Optional device binding for TOTP"
    )


class TOTPProvisionResponse(BaseModel):
    """Response with TOTP provisioning details."""

    totp_secret_id: int
    provisioning_uri: str = Field(description="otpauth:// URI for QR code")
    expires_at: str = Field(description="ISO timestamp when QR expires")
    secret: str = Field(description="Base32 secret for manual entry (optional)")


class TOTPActivateRequest(BaseModel):
    """Request to activate TOTP after scanning QR code."""

    totp_secret_id: int
    verification_code: str = Field(
        min_length=6, max_length=8, description="6 or 8-digit TOTP code"
    )


class TOTPActivateResponse(BaseModel):
    """Response after TOTP activation."""

    success: bool
    message: str
    recovery_codes: list[str] = Field(
        description="5 single-use recovery codes (show once!)"
    )


class TOTPValidateRequest(BaseModel):
    """Request to validate TOTP code (for kiosk/punch)."""

    totp_code: str = Field(min_length=6, max_length=8, description="TOTP code")
    kiosk_id: Optional[int] = Field(default=None, description="Kiosk ID")
    nonce: Optional[str] = Field(
        default=None, description="Nonce for replay protection"
    )
    jwt_jti: Optional[str] = Field(default=None, description="JWT ID for correlation")


class TOTPValidateResponse(BaseModel):
    """Response after TOTP validation."""

    success: bool
    message: str
    time_offset_periods: Optional[int] = Field(
        default=None, description="Time offset if valid (0=current, ±N=offset)"
    )


class RecoveryCodeUseRequest(BaseModel):
    """Request to use recovery code."""

    recovery_code: str = Field(description="Recovery code (e.g., ABCD-EFGH)")


class RecoveryCodeUseResponse(BaseModel):
    """Response after using recovery code."""

    success: bool
    message: str


class RecoveryCodesStatusResponse(BaseModel):
    """Recovery codes status."""

    total: int
    unused: int
    used: int
    expired: int
    hints: list[str] = Field(description="Hints for unused codes (first 4 chars)")


class RecoveryCodesRegenerateResponse(BaseModel):
    """Response with new recovery codes."""

    recovery_codes: list[str] = Field(description="New recovery codes (show once!)")
    message: str


# --- Endpoints ---


@router.post("/provision", response_model=TOTPProvisionResponse)
def provision_totp(
    request: TOTPProvisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Initiate TOTP provisioning (generate secret and QR URI).

    Returns otpauth:// URI for QR code generation.
    QR code expires in 300 seconds (5 minutes).

    Raises:
        400: User already has active TOTP
    """
    try:
        result = initiate_totp_provisioning(
            db=db,
            user_id=current_user.id,
            device_id=request.device_id,
            encryption_key_id="default",
            provisioning_expiry_seconds=300,
        )

        return TOTPProvisionResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/activate", response_model=TOTPActivateResponse)
def activate_totp_endpoint(
    request: TOTPActivateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Activate TOTP after scanning QR code.

    Verifies first TOTP code and generates 5 recovery codes.

    Raises:
        400: Invalid verification code or expired provisioning
        404: TOTP secret not found
    """
    try:
        # Activate TOTP
        success = activate_totp(
            db=db,
            totp_secret_id=request.totp_secret_id,
            verification_code=request.verification_code,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        # Generate recovery codes
        recovery_codes = create_recovery_codes(
            db=db, totp_secret_id=request.totp_secret_id, count=5
        )

        return TOTPActivateResponse(
            success=True,
            message="TOTP activated successfully. Save recovery codes in a safe place!",
            recovery_codes=recovery_codes,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/validate", response_model=TOTPValidateResponse)
def validate_totp_endpoint(
    request: TOTPValidateRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Validate TOTP code (for time tracking punch).

    Implements security controls:
    - Rate limiting: 5 attempts / 10 minutes
    - Account lockout: 15 minutes after rate limit exceeded
    - Replay protection: nonce blacklist
    - Monitoring: alert on 3 failed attempts / 10 minutes

    Raises:
        400: Invalid TOTP code
        403: Account locked or rate limit exceeded
        404: User has no active TOTP
    """
    user_id = current_user.id
    ip_address = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("user-agent")

    try:
        # 1. Check account lockout
        check_account_lockout(db, user_id)

        # 2. Check rate limiting
        check_rate_limit(db, user_id, window_minutes=10, max_attempts=5)

        # 3. Check replay protection (nonce blacklist)
        if request.nonce and is_nonce_blacklisted(db, request.nonce):
            record_validation_attempt(
                db=db,
                user_id=user_id,
                is_success=False,
                failure_reason="nonce_blacklisted",
                kiosk_id=request.kiosk_id,
                ip_address=ip_address,
                user_agent=user_agent,
                jwt_jti=request.jwt_jti,
                nonce=request.nonce,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Replay attack detected (nonce already used)",
            )

        # 4. Get active TOTP secret
        totp_secret = db.execute(
            select(TOTPSecret).where(
                TOTPSecret.user_id == user_id,
                TOTPSecret.is_active == True,  # noqa: E712
                TOTPSecret.is_activated == True,  # noqa: E712
            )
        ).first()

        if not totp_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active TOTP found. Please provision TOTP first.",
            )

        # 5. Decrypt secret and validate code
        secret = decrypt_secret(totp_secret.encrypted_secret)
        from src.totp.core import verify_totp_code

        is_valid, time_offset = verify_totp_code(
            secret=secret,
            code=request.totp_code,
            period=totp_secret.period,
            digits=totp_secret.digits,
            algorithm=totp_secret.algorithm,
            window=1,  # Allow ±1 period (30s before/after)
        )

        # 6. Record validation attempt
        if is_valid:
            # Success - blacklist nonce
            if request.nonce:
                blacklist_nonce(
                    db=db,
                    nonce=request.nonce,
                    user_id=user_id,
                    jwt_jti=request.jwt_jti or "",
                    jwt_expires_at=datetime.utcnow(),
                    kiosk_id=request.kiosk_id,
                    ip_address=ip_address,
                )

            record_validation_attempt(
                db=db,
                user_id=user_id,
                is_success=True,
                kiosk_id=request.kiosk_id,
                ip_address=ip_address,
                user_agent=user_agent,
                jwt_jti=request.jwt_jti,
                nonce=request.nonce,
            )

            # Update last_used_at
            totp_secret.last_used_at = datetime.utcnow()
            db.commit()

            return TOTPValidateResponse(
                success=True,
                message="TOTP code validated successfully",
                time_offset_periods=time_offset,
            )
        else:
            # Failure - record and check for lockout
            record_validation_attempt(
                db=db,
                user_id=user_id,
                is_success=False,
                failure_reason="invalid_code",
                kiosk_id=request.kiosk_id,
                ip_address=ip_address,
                user_agent=user_agent,
                jwt_jti=request.jwt_jti,
                nonce=request.nonce,
            )

            # Check if should trigger alert
            if should_trigger_alert(db, user_id, window_minutes=10, threshold=3):
                # TODO: Send security alert (email, Slack, etc.)
                pass

            # Check if should trigger lockout
            failed_count = get_failed_attempts_count(db, user_id, window_minutes=10)
            if failed_count >= 5:
                trigger_lockout(
                    db=db,
                    user_id=user_id,
                    lockout_minutes=15,
                    trigger_reason="rate_limit",
                    ip_address=ip_address,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account locked for 15 minutes due to excessive failures",
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code",
            )

    except AccountLocked as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RateLimitExceeded as e:
        # Trigger lockout
        trigger_lockout(
            db=db,
            user_id=user_id,
            lockout_minutes=15,
            trigger_reason="rate_limit",
            ip_address=ip_address,
        )
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))


@router.post("/recovery/use", response_model=RecoveryCodeUseResponse)
def use_recovery_code_endpoint(
    request: RecoveryCodeUseRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Use a recovery code for authentication bypass.

    Recovery codes are single-use and should be used sparingly.

    Raises:
        400: Invalid recovery code
    """
    ip_address = http_request.client.host if http_request.client else None

    success = use_recovery_code(
        db=db,
        user_id=current_user.id,
        code=request.recovery_code,
        ip_address=ip_address,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired recovery code",
        )

    return RecoveryCodeUseResponse(
        success=True, message="Recovery code used successfully"
    )


@router.get("/recovery/status", response_model=RecoveryCodesStatusResponse)
def get_recovery_status_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get status of recovery codes."""
    status_data = get_recovery_codes_status(db, user_id=current_user.id)
    return RecoveryCodesStatusResponse(**status_data)


@router.post("/recovery/regenerate", response_model=RecoveryCodesRegenerateResponse)
def regenerate_recovery_codes_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Regenerate recovery codes (invalidate old ones).

    Returns new recovery codes. Old unused codes will be invalidated.

    Raises:
        404: No active TOTP found
    """
    # Get active TOTP secret
    totp_secret = db.execute(
        select(TOTPSecret).where(
            TOTPSecret.user_id == current_user.id,
            TOTPSecret.is_active == True,  # noqa: E712
            TOTPSecret.is_activated == True,  # noqa: E712
        )
    ).first()

    if not totp_secret:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active TOTP found",
        )

    new_codes = regenerate_recovery_codes(
        db=db,
        user_id=current_user.id,
        totp_secret_id=totp_secret.id,
        count=5,
    )

    return RecoveryCodesRegenerateResponse(
        recovery_codes=new_codes,
        message="Recovery codes regenerated successfully. Save them in a safe place!",
    )
