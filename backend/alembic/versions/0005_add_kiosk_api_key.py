"""add api_key_hash to kiosks

Revision ID: 0005_add_kiosk_api_key
Revises: 0003_add_chrona_tables
Create Date: 2025-10-19
"""

import sqlalchemy as sa

from alembic import op

revision = "0005_add_kiosk_api_key"
down_revision = "0003_add_chrona_tables"
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
