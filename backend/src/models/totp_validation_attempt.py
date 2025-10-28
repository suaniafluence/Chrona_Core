"""TOTP Validation Attempt model for rate limiting and security monitoring."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TOTPValidationAttempt(SQLModel, table=True):
    """TOTP validation attempts for rate limiting and incident detection.

    Tracks all TOTP validation attempts (success/failure) for security monitoring.
    Compliant with kiosk security spec:
    - rate_limit: 5 attempts / 10min
    - lockout: 15min
    - monitoring.detect_duplication: true
    - monitoring.alert_threshold: 3 failed / 10min
    - logging: exclude [secret, otp], include [uid, scanner_id, timestamp, outcome]
    """

    __tablename__ = "totp_validation_attempts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User ID attempting TOTP validation",
    )
    kiosk_id: Optional[int] = Field(
        default=None,
        foreign_key="kiosks.id",
        index=True,
        description="Kiosk/scanner ID",
    )

    # Attempt details (exclude sensitive data per spec)
    is_success: bool = Field(
        nullable=False,
        index=True,
        description="Whether validation succeeded",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Failure reason (invalid_code, expired, rate_limited, etc.)",
    )

    # Timestamps for rate limiting windows
    attempted_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When validation was attempted",
    )

    # Network metadata (for incident response)
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        index=True,
        description="IP address of request",
    )
    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description="User agent string",
    )

    # Duplication detection
    jwt_jti: Optional[str] = Field(
        default=None,
        max_length=255,
        index=True,
        description="JWT ID for duplication detection (replay attacks)",
    )
    nonce: Optional[str] = Field(
        default=None,
        max_length=255,
        index=True,
        description="Nonce for duplication detection",
    )
