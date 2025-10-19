"""add api_key_hash to kiosks

Revision ID: 0005_add_kiosk_api_key
Revises: 0004_use_punch_enum
Create Date: 2025-10-19
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_kiosk_api_key"
down_revision = "0004_use_punch_enum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add api_key_hash column to kiosks table
    op.add_column(
        "kiosks",
        sa.Column("api_key_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    # Remove api_key_hash column
    op.drop_column("kiosks", "api_key_hash")
