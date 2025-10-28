"""TOTP Recovery Code model for account recovery."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TOTPRecoveryCode(SQLModel, table=True):
    """Recovery codes for TOTP authentication bypass.

    Single-use backup codes (5 per user) for emergency access.
    Compliant with security spec:
    - codes_backup: 5 (usage unique)
    - reset_process: email + sms + ID vérif
    """

    __tablename__ = "totp_recovery_codes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User ID (employee)",
    )
    totp_secret_id: int = Field(
        foreign_key="totp_secrets.id",
        index=True,
        nullable=False,
        description="Associated TOTP secret",
    )

    # Recovery code (hashed for security)
    code_hash: str = Field(
        nullable=False,
        description="Hashed recovery code (PBKDF2-HMAC-SHA256)",
    )
    code_hint: str = Field(
        max_length=10,
        nullable=False,
        description="First 4 characters for display (e.g., 'ABCD-****')",
    )

    # Usage tracking
    is_used: bool = Field(
        default=False,
        index=True,
        nullable=False,
        description="Whether recovery code has been used",
    )
    used_at: Optional[datetime] = Field(
        default=None,
        description="When recovery code was used",
    )
    used_from_ip: Optional[str] = Field(
        default=None,
        max_length=45,
        description="IP address where code was used",
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Recovery code generation timestamp",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Optional expiration for recovery codes",
    )
