"""add kiosk access control

Revision ID: 0008_add_kiosk_access_control
Revises: 0007_add_kiosk_heartbeat
Create Date: 2025-10-26
"""

import sqlalchemy as sa

from alembic import op

revision = "0008_add_kiosk_access_control"
down_revision = "0007_add_kiosk_heartbeat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add access_mode column to kiosks table
    op.add_column(
        "kiosks",
        sa.Column(
            "access_mode",
            sa.String(length=20),
            server_default="public",
            nullable=False,
        ),
    )

    # Create kiosk_access table
    op.create_table(
        "kiosk_access",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kiosk_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("granted_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("granted_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["granted_by_admin_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kiosk_id"],
            ["kiosks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kiosk_id", "user_id", name="uq_kiosk_user"),
    )
    op.create_index(
        "ix_kiosk_access_kiosk_id", "kiosk_access", ["kiosk_id"], unique=False
    )
    op.create_index(
        "ix_kiosk_access_user_id", "kiosk_access", ["user_id"], unique=False
    )


def downgrade() -> None:
    # Remove kiosk_access table
    op.drop_index("ix_kiosk_access_user_id", table_name="kiosk_access")
    op.drop_index("ix_kiosk_access_kiosk_id", table_name="kiosk_access")
    op.drop_table("kiosk_access")

    # Remove access_mode column
    op.drop_column("kiosks", "access_mode")
