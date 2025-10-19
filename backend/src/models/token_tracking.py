"""Token tracking model for nonce and JTI single-use enforcement."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TokenTracking(SQLModel, table=True):
    """Track ephemeral tokens to enforce single-use and prevent replay attacks."""

    __tablename__ = "token_tracking"

    jti: str = Field(
        primary_key=True,
        max_length=255,
        nullable=False,
        description="Unique token ID (JWT jti claim)",
    )
    nonce: str = Field(
        index=True,
        max_length=255,
        nullable=False,
        description="Random nonce value for replay protection",
    )
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    device_id: int = Field(foreign_key="devices.id", index=True, nullable=False)
    issued_at: datetime = Field(
        nullable=False, description="Token issue timestamp (iat)"
    )
    expires_at: datetime = Field(
        index=True, nullable=False, description="Token expiration timestamp (exp)"
    )
    consumed_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Timestamp when token was consumed (null if unused)",
    )
    consumed_by_kiosk_id: Optional[int] = Field(
        default=None,
        foreign_key="kiosks.id",
        nullable=True,
        description="Kiosk ID that consumed the token (null if unused)",
    )
