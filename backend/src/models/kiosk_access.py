"""Kiosk access control models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint


class KioskAccessMode(str, Enum):
    """Access control modes for kiosks."""

    PUBLIC = "public"  # Everyone can access
    WHITELIST = "whitelist"  # Only specific users allowed
    BLACKLIST = "blacklist"  # Everyone except specific users


class KioskAccess(SQLModel, table=True):
    """User-kiosk access permissions."""

    __tablename__ = "kiosk_access"

    id: Optional[int] = Field(default=None, primary_key=True)
    kiosk_id: int = Field(
        foreign_key="kiosks.id", index=True, nullable=False, description="Kiosk ID"
    )
    user_id: int = Field(
        foreign_key="users.id", index=True, nullable=False, description="User ID"
    )
    granted: bool = Field(
        default=True,
        nullable=False,
        description="True=authorized, False=blocked (for blacklist mode)",
    )
    granted_by_admin_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        description="Admin who granted the access",
    )
    granted_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When access was granted",
    )
    expires_at: Optional[datetime] = Field(
        default=None, nullable=True, description="Optional expiration date for access"
    )

    __table_args__ = (UniqueConstraint("kiosk_id", "user_id", name="uq_kiosk_user"),)
