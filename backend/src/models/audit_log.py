"""Audit log model for immutable security event tracking."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    """Immutable security audit trail for compliance and forensics."""

    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(
        index=True,
        max_length=100,
        nullable=False,
        description=(
            "Type of event (e.g., 'punch_validated', "
            "'device_revoked', 'login_failed')"
        ),
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", index=True, nullable=True
    )
    device_id: Optional[int] = Field(
        default=None, foreign_key="devices.id", index=True, nullable=True
    )
    kiosk_id: Optional[int] = Field(
        default=None, foreign_key="kiosks.id", index=True, nullable=True
    )
    event_data: Optional[str] = Field(
        default=None,
        description="JSON blob with event details",
    )
    ip_address: Optional[str] = Field(
        default=None, max_length=45, description="Source IP address (IPv4 or IPv6)"
    )
    user_agent: Optional[str] = Field(
        default=None, max_length=500, description="Client user agent string"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        nullable=False,
        description="Event timestamp",
    )

    # Note: This table should be append-only (no updates/deletes)
    # Implement database trigger: BEFORE UPDATE/DELETE -> RAISE EXCEPTION
