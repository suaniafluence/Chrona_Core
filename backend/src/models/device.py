"""Device model for registered employee devices."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Device(SQLModel, table=True):
    """Registered employee device for time tracking."""

    __tablename__ = "devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    device_fingerprint: str = Field(
        index=True,
        unique=True,
        max_length=255,
        nullable=False,
        description="Unique device identifier (hashed)",
    )
    device_name: str = Field(
        max_length=100, nullable=False, description="Human-readable device name"
    )
    attestation_data: Optional[str] = Field(
        default=None,
        description="JSON blob with SafetyNet/DeviceCheck attestation data",
    )
    registered_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Device registration timestamp",
    )
    last_seen_at: Optional[datetime] = Field(
        default=None, description="Last activity timestamp"
    )
    is_revoked: bool = Field(
        default=False, index=True, nullable=False, description="Device revocation flag"
    )

    # Relationships (if User model has back_populates)
    # user: "User" = Relationship(back_populates="devices")
