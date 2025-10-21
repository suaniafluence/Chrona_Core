"""Onboarding Session model to track multi-step onboarding flow."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class OnboardingSession(SQLModel, table=True):
    """Track onboarding progress for Level B security flow."""

    __tablename__ = "onboarding_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_token: str = Field(
        index=True,
        unique=True,
        max_length=255,
        nullable=False,
        description="Unique session token for onboarding flow",
    )
    email: str = Field(
        index=True,
        max_length=255,
        nullable=False,
        description="Employee email being onboarded",
    )
    hr_code_id: Optional[int] = Field(
        default=None,
        foreign_key="hr_codes.id",
        description="Associated HR code",
    )
    step: str = Field(
        default="hr_code",
        max_length=50,
        nullable=False,
        description=(
            "Current step: hr_code, otp_sent, otp_verified, "
            "device_attestation, completed"
        ),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Session start timestamp",
    )
    expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="Session expiration (e.g., 30 minutes)",
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="When onboarding completed"
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        description="IP address of session",
    )
    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description="User agent string",
    )
    device_fingerprint_candidate: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Device fingerprint being registered",
    )
