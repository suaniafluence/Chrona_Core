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
