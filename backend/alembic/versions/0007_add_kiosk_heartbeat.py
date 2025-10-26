"""add heartbeat fields to kiosks

Revision ID: 0007_add_kiosk_heartbeat
Revises: 0006_add_onboarding_tables
Create Date: 2025-10-26
"""

import sqlalchemy as sa

from alembic import op

revision = "0007_add_kiosk_heartbeat"
down_revision = "0006_add_onboarding_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add heartbeat tracking columns to kiosks table
    op.add_column(
        "kiosks",
        sa.Column("last_heartbeat_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "kiosks",
        sa.Column("app_version", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "kiosks",
        sa.Column("device_info", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    # Remove heartbeat tracking columns
    op.drop_column("kiosks", "device_info")
    op.drop_column("kiosks", "app_version")
    op.drop_column("kiosks", "last_heartbeat_at")
