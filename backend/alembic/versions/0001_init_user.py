"""init user table

Revision ID: 0001_init_user
Revises: 
Create Date: 2025-10-18
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = "0001_init_user"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, nullable=False, unique=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.utcnow),
    )


def downgrade() -> None:
    op.drop_table("user")

