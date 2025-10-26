"""Kiosk model for authorized tablet scanning stations."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Kiosk(SQLModel, table=True):
    """Authorized kiosk tablet for QR code scanning."""

    __tablename__ = "kiosks"

    id: Optional[int] = Field(default=None, primary_key=True)
    kiosk_name: str = Field(
        unique=True,
        index=True,
        max_length=100,
        nullable=False,
        description="Unique kiosk identifier (e.g., 'Entrance-Floor1')",
    )
    location: str = Field(
        max_length=255, nullable=False, description="Physical location description"
    )
    device_fingerprint: str = Field(
        unique=True,
        index=True,
        max_length=255,
        nullable=False,
        description="Kiosk hardware identifier",
    )
    public_key: Optional[str] = Field(
        default=None,
        description="Optional RS256 public key for validation",
    )
    api_key_hash: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="Hashed API key for kiosk authentication (bcrypt)",
    )
    is_active: bool = Field(
        default=True, index=True, nullable=False, description="Active status flag"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Registration timestamp",
    )
    last_heartbeat_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Last heartbeat/ping timestamp",
    )
    app_version: Optional[str] = Field(
        default=None,
        max_length=50,
        nullable=True,
        description="Mobile app version",
    )
    device_info: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="Device model and OS info",
    )
    access_mode: str = Field(
        default="public",
        max_length=20,
        nullable=False,
        description="Access control mode: public, whitelist, or blacklist",
    )
