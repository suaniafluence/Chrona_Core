"""Add IP address field to kiosks for IP-based identification.

Revision ID: 0010_add_kiosk_ip_address
Revises: 0009_add_totp_tables
Create Date: 2025-10-29 17:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0010_add_kiosk_ip_address"
down_revision = "0009_add_totp_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ip_address column to kiosks table."""
    # For SQLite batch mode is required for column constraints
    with op.batch_alter_table("kiosks") as batch_op:
        # Add ip_address column with unique constraint
        batch_op.add_column(
            sa.Column(
                "ip_address",
                sa.String(length=45),
                nullable=True,
                unique=True,
                index=True,
            )
        )


def downgrade() -> None:
    """Remove ip_address column from kiosks table."""
    with op.batch_alter_table("kiosks") as batch_op:
        batch_op.drop_column("ip_address")
