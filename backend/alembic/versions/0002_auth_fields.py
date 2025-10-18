"""add auth fields to user

Revision ID: 0002_auth_fields
Revises: 0001_init_user
Create Date: 2025-10-18
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_auth_fields"
down_revision = "0001_init_user"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("hashed_password", sa.String(), nullable=False, server_default=""))
    op.add_column("user", sa.Column("role", sa.String(), nullable=False, server_default="user"))
    # remove server_default after backfilling
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column("hashed_password", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_column("role")
        batch_op.drop_column("hashed_password")

