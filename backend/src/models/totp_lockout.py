"""TOTP Lockout model for user account security."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TOTPLockout(SQLModel, table=True):
    """TOTP account lockouts after excessive failed attempts.

    Implements 15-minute lockout after rate limit exceeded.
    Compliant with kiosk security spec:
    - rate_limit: 5 attempts / 10min
    - lockout: 15min
    """

    __tablename__ = "totp_lockouts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        unique=True,  # One active lockout per user
        nullable=False,
        description="User ID under lockout",
    )

    # Lockout period
    locked_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When lockout started",
    )
    locked_until: datetime = Field(
        nullable=False,
        index=True,
        description="When lockout expires (15 minutes from locked_at)",
    )

    # Lockout reason
    failed_attempts_count: int = Field(
        nullable=False,
        description="Number of failed attempts that triggered lockout",
    )
    trigger_reason: str = Field(
        max_length=100,
        nullable=False,
        description="Lockout trigger reason (rate_limit, security_incident, etc.)",
    )

    # Status
    is_active: bool = Field(
        default=True,
        index=True,
        nullable=False,
        description="Whether lockout is currently active",
    )
    released_at: Optional[datetime] = Field(
        default=None,
        description="When lockout was released (null if still locked)",
    )
    released_by: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Who released lockout (system, admin_email, etc.)",
    )

    # Audit
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        description="IP address associated with failed attempts",
    )
