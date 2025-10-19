"""Punch model for attendance events (clock-in/clock-out)."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class PunchType(str, Enum):
    """Type of punch event."""

    CLOCK_IN = "clock_in"
    CLOCK_OUT = "clock_out"


class Punch(SQLModel, table=True):
    """Attendance event record."""

    __tablename__ = "punches"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    device_id: int = Field(foreign_key="devices.id", index=True, nullable=False)
    kiosk_id: int = Field(foreign_key="kiosks.id", index=True, nullable=False)
    punch_type: PunchType = Field(
        nullable=False,
        description="Type of punch (clock_in or clock_out)",
    )
    punched_at: datetime = Field(
        index=True, nullable=False, description="Timestamp of the punch event"
    )
    jwt_jti: str = Field(
        unique=True,
        max_length=255,
        nullable=False,
        description="JTI from validated JWT (for traceability)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Record creation timestamp",
    )
