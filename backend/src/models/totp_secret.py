"""TOTP Secret model for employee TOTP authentication."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TOTPSecret(SQLModel, table=True):
    """TOTP secret for employee time tracking authentication.

    Stores encrypted TOTP secrets with device binding and provisioning metadata.
    Compliant with:
    - Entropy: ≥160 bits
    - Encoding: Base32
    - Storage: Encrypted (AES-GCM)
    - Algorithm: SHA256
    """

    __tablename__ = "totp_secrets"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="User ID (employee)",
    )
    device_id: Optional[int] = Field(
        default=None,
        foreign_key="devices.id",
        index=True,
        description="Optional device binding for TOTP",
    )

    # Encrypted TOTP secret (Base32 encoded, encrypted with AES-GCM)
    encrypted_secret: str = Field(
        nullable=False,
        description="AES-GCM encrypted TOTP secret (Base32)",
    )
    encryption_key_id: str = Field(
        max_length=100,
        nullable=False,
        description="Key ID for KMS/HSM encryption key (for rotation)",
    )

    # TOTP configuration
    algorithm: str = Field(
        default="SHA256",
        max_length=20,
        nullable=False,
        description="TOTP hash algorithm (SHA1/SHA256/SHA512)",
    )
    digits: int = Field(
        default=6,
        nullable=False,
        description="Number of TOTP digits (6 or 8)",
    )
    period: int = Field(
        default=30,
        nullable=False,
        description="TOTP time period in seconds",
    )

    # Provisioning metadata
    provisioning_qr_expires_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="QR code provisioning expiry (300s from creation)",
    )
    is_activated: bool = Field(
        default=False,
        index=True,
        nullable=False,
        description="Whether TOTP has been activated (first code validated)",
    )
    activated_at: Optional[datetime] = Field(
        default=None,
        description="When TOTP was activated",
    )

    # Status and metadata
    is_active: bool = Field(
        default=True,
        index=True,
        nullable=False,
        description="Whether TOTP is active (can be disabled by admin)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Secret creation timestamp",
    )
    last_used_at: Optional[datetime] = Field(
        default=None,
        description="Last successful TOTP validation",
    )

    # Key rotation
    key_rotation_due_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Next key rotation deadline (90 days)",
    )
