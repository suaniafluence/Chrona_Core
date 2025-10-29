from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

try:
    # Pydantic v2
    from pydantic import ConfigDict  # type: ignore
except Exception:  # pragma: no cover
    ConfigDict = dict  # fallback for type checking

from src.models.punch import PunchType


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # allow ORM objects
    id: int
    email: EmailStr
    role: str
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str


# ==================== Device Schemas ====================


class DeviceCreate(BaseModel):
    """Schema for registering a new device."""

    device_fingerprint: str = Field(
        ..., max_length=255, description="Unique device identifier (hashed)"
    )
    device_name: str = Field(
        ..., max_length=100, description="Human-readable device name"
    )
    attestation_data: Optional[str] = Field(
        None, description="JSON blob with SafetyNet/DeviceCheck attestation"
    )


class DeviceRead(BaseModel):
    """Schema for reading device information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_fingerprint: str
    device_name: str
    attestation_data: Optional[str]
    registered_at: datetime
    last_seen_at: Optional[datetime]
    is_revoked: bool


class DeviceUpdate(BaseModel):
    """Schema for updating device information."""

    device_name: Optional[str] = Field(None, max_length=100)
    is_revoked: Optional[bool] = None


# ==================== Kiosk Schemas ====================


class KioskCreate(BaseModel):
    """Schema for creating a new kiosk."""

    kiosk_name: str = Field(..., max_length=100)
    location: str = Field(..., max_length=255)
    device_fingerprint: str = Field(
        ..., max_length=255, description="Android device ID or IMEI"
    )
    ip_address: Optional[str] = Field(
        None, max_length=45, description="Static IP address (IPv4 or IPv6)"
    )
    public_key: Optional[str] = Field(
        None, description="RSA public key for JWT verification"
    )


class KioskRead(BaseModel):
    """Schema for reading kiosk information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    kiosk_name: str
    location: str
    device_fingerprint: str
    ip_address: Optional[str]
    public_key: Optional[str]
    is_active: bool
    created_at: datetime
    last_heartbeat_at: Optional[datetime]


class KioskUpdate(BaseModel):
    """Schema for updating kiosk information."""

    kiosk_name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(
        None, max_length=45, description="Update static IP address"
    )
    is_active: Optional[bool] = None


# ==================== Punch Schemas ====================


class QRTokenRequest(BaseModel):
    """Schema for requesting an ephemeral QR token."""

    device_id: int = Field(..., description="ID of the device making request")


class QRTokenResponse(BaseModel):
    """Schema for ephemeral QR token response."""

    qr_token: str = Field(..., description="JWT token to encode in QR")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: datetime = Field(..., description="Absolute expiration time")


class PunchValidateRequest(BaseModel):
    """Schema for validating a QR code punch."""

    qr_token: str = Field(..., description="JWT token scanned from QR")
    kiosk_id: int = Field(..., description="ID of kiosk scanning QR")
    punch_type: PunchType = Field(..., description="clock_in or clock_out")


class PunchValidateResponse(BaseModel):
    """Schema for punch validation response."""

    success: bool
    message: str
    punch_id: Optional[int] = None
    punched_at: Optional[datetime] = None
    user_id: Optional[int] = None
    device_id: Optional[int] = None
    punch_type: Optional[PunchType] = None


class PunchCreate(BaseModel):
    """Schema for creating a punch record (internal use)."""

    user_id: int
    device_id: int
    kiosk_id: int
    punch_type: PunchType
    jwt_jti: str


class PunchRead(BaseModel):
    """Schema for reading punch records."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_id: int
    kiosk_id: int
    punch_type: PunchType
    punched_at: datetime
    jwt_jti: str
    created_at: datetime


# ==================== Audit Log Schemas ====================


class AuditLogRead(BaseModel):
    """Schema for reading audit log entries."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    user_id: Optional[int]
    device_id: Optional[int]
    kiosk_id: Optional[int]
    event_data: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


# ==================== Onboarding Schemas (Level B) ====================


class HRCodeCreate(BaseModel):
    """Schema for creating an HR code (admin only)."""

    employee_email: EmailStr = Field(..., description="Employee email address")
    employee_name: Optional[str] = Field(None, max_length=255)
    expires_in_days: int = Field(7, ge=1, le=30, description="Expiration in days")


class HRCodeRead(BaseModel):
    """Schema for reading HR code information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    employee_email: EmailStr
    employee_name: Optional[str]
    created_by_admin_id: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]
    is_used: bool
    used_at: Optional[datetime]
    used_by_user_id: Optional[int]


class OnboardingInitiateRequest(BaseModel):
    """Schema for initiating onboarding with HR code."""

    hr_code: str = Field(..., max_length=20, description="HR-provided code")
    email: EmailStr = Field(..., description="Employee email address")


class OnboardingInitiateResponse(BaseModel):
    """Schema for onboarding initiation response."""

    success: bool
    message: str
    session_token: Optional[str] = Field(
        None, description="Session token for onboarding flow"
    )
    step: Optional[str] = Field(None, description="Current onboarding step")


class OnboardingVerifyOTPRequest(BaseModel):
    """Schema for OTP verification during onboarding."""

    session_token: str = Field(..., description="Onboarding session token")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")


class OnboardingVerifyOTPResponse(BaseModel):
    """Schema for OTP verification response."""

    success: bool
    message: str
    step: Optional[str] = Field(None, description="Next onboarding step")


class OnboardingCompleteRequest(BaseModel):
    """Schema for completing onboarding with device attestation."""

    session_token: str = Field(..., description="Onboarding session token")
    password: str = Field(..., min_length=8, description="Account password")
    device_fingerprint: str = Field(..., max_length=255)
    device_name: str = Field(..., max_length=100)
    attestation_data: Optional[str] = Field(
        None, description="SafetyNet/DeviceCheck attestation"
    )


class OnboardingCompleteResponse(BaseModel):
    """Schema for onboarding completion response."""

    success: bool
    message: str
    user_id: Optional[int] = None
    device_id: Optional[int] = None
    access_token: Optional[str] = Field(None, description="JWT access token")
