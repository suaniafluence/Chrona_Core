"""HR Code model for Level B onboarding."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class HRCode(SQLModel, table=True):
    """HR-generated codes for employee onboarding (Level B security)."""

    __tablename__ = "hr_codes"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(
        index=True,
        unique=True,
        max_length=20,
        nullable=False,
        description="Unique HR code (e.g., EMPL-2024-001)",
    )
    employee_email: str = Field(
        index=True,
        max_length=255,
        nullable=False,
        description="Pre-registered employee email",
    )
    employee_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Employee full name",
    )
    created_by_admin_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        description="Admin who generated the code",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Code generation timestamp",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Code expiration (optional, e.g., 7 days)",
    )
    is_used: bool = Field(
        default=False,
        index=True,
        nullable=False,
        description="Whether code has been redeemed",
    )
    used_at: Optional[datetime] = Field(default=None, description="When code was used")
    used_by_user_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        description="User who redeemed the code",
    )
