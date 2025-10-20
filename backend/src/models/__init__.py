from sqlmodel import SQLModel

from .audit_log import AuditLog
from .device import Device
from .hr_code import HRCode
from .kiosk import Kiosk
from .onboarding_session import OnboardingSession
from .otp_verification import OTPVerification
from .punch import Punch, PunchType
from .token_tracking import TokenTracking
from .user import User

# Re-export metadata for Alembic
metadata = SQLModel.metadata

__all__ = [
    "AuditLog",
    "Device",
    "HRCode",
    "Kiosk",
    "OnboardingSession",
    "OTPVerification",
    "Punch",
    "PunchType",
    "TokenTracking",
    "User",
    "SQLModel",
    "metadata",
]
