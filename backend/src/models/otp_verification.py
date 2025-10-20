"""OTP Verification model for Level B onboarding."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class OTPVerification(SQLModel, table=True):
    """OTP tokens for two-factor authentication during onboarding."""

    __tablename__ = "otp_verifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(
        index=True,
        max_length=255,
        nullable=False,
        description="Email address for OTP delivery",
    )
    otp_code: str = Field(
        max_length=10,
        nullable=False,
        description="OTP code (e.g., 6-digit numeric)",
    )
    otp_hash: str = Field(
        nullable=False,
        description="Hashed OTP for secure verification",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="OTP generation timestamp",
    )
    expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="OTP expiration (e.g., 10 minutes)",
    )
    is_verified: bool = Field(
        default=False,
        index=True,
        nullable=False,
        description="Whether OTP has been successfully verified",
    )
    verified_at: Optional[datetime] = Field(
        default=None, description="When OTP was verified"
    )
    attempt_count: int = Field(
        default=0,
        nullable=False,
        description="Number of verification attempts (rate limiting)",
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        description="IP address of request",
    )
    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description="User agent string",
    )
