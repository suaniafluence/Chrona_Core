"""TOTP Nonce Blacklist for replay attack protection."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TOTPNonceBlacklist(SQLModel, table=True):
    """Nonce blacklist for TOTP JWT replay protection.

    Tracks used nonces to prevent QR code replay attacks.
    Compliant with kiosk security spec:
    - replay_protection: nonce blacklist
    - JWT format: [iss, uid, nonce, exp]
    - exp: 30s
    """

    __tablename__ = "totp_nonce_blacklist"

    nonce: str = Field(
        primary_key=True,
        max_length=255,
        nullable=False,
        description="Unique nonce from TOTP JWT",
    )
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User ID for audit trail",
    )
    kiosk_id: Optional[int] = Field(
        default=None,
        foreign_key="kiosks.id",
        index=True,
        description="Kiosk that consumed the nonce",
    )

    # JWT metadata
    jwt_jti: str = Field(
        index=True,
        max_length=255,
        nullable=False,
        description="JWT ID (jti claim) for correlation",
    )
    jwt_expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="JWT expiration timestamp (for cleanup)",
    )

    # Usage tracking
    consumed_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When nonce was consumed (blacklisted)",
    )
    consumed_from_ip: Optional[str] = Field(
        default=None,
        max_length=45,
        description="IP address of kiosk/scanner",
    )
