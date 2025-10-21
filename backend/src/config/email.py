"""Email configuration for OTP and notifications."""

from enum import Enum
from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class EmailProvider(str, Enum):
    """Supported email providers."""

    SMTP = "smtp"
    SENDGRID = "sendgrid"
    CONSOLE = "console"  # For development/testing


class EmailSettings(BaseSettings):
    """Email service configuration."""

    # Provider selection
    EMAIL_PROVIDER: EmailProvider = EmailProvider.CONSOLE

    # SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True

    # SendGrid Configuration
    SENDGRID_API_KEY: Optional[str] = None

    # Email sender details
    EMAIL_FROM_ADDRESS: EmailStr = "noreply@chrona.com"
    EMAIL_FROM_NAME: str = "Chrona - Time Tracking"

    # Email templates
    OTP_SUBJECT: str = "Votre code de vérification Chrona"
    OTP_EXPIRY_MINUTES: int = 10

    # Development settings
    EMAIL_TEST_MODE: bool = False  # If True, emails are logged but not sent
    EMAIL_TEST_RECIPIENT: Optional[EmailStr] = None  # Override recipient in test mode

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
email_settings = EmailSettings()


def get_email_settings() -> EmailSettings:
    """Get email settings instance.

    Returns:
        EmailSettings instance
    """
    return email_settings
