"""use PostgreSQL ENUM for punch_type

Revision ID: 0004_use_punch_enum
Revises: 0003_add_chrona_tables
Create Date: 2025-10-19
"""

import sqlalchemy as sa

from alembic import op

revision = "0004_use_punch_enum"
down_revision = "0003_add_chrona_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Define the ENUM to match SQLAlchemy's native enum storage (uses member NAMES)
    punch_enum = sa.Enum("CLOCK_IN", "CLOCK_OUT", name="punchtype")
    bind = op.get_bind()
    punch_enum.create(bind, checkfirst=True)

    # Alter column to use ENUM, casting existing text values if any
    op.alter_column(
        "punches",
        "punch_type",
        existing_type=sa.String(length=20),
        type_=punch_enum,
        postgresql_using="punch_type::text::punchtype",
        existing_nullable=False,
    )


def downgrade() -> None:
    # Revert column back to text and drop ENUM type
    bind = op.get_bind()
    op.alter_column(
        "punches",
        "punch_type",
        existing_type=sa.Enum("CLOCK_IN", "CLOCK_OUT", name="punchtype"),
        type_=sa.String(length=20),
        postgresql_using="punch_type::text",
        existing_nullable=False,
    )

    punch_enum = sa.Enum("CLOCK_IN", "CLOCK_OUT", name="punchtype")
    punch_enum.drop(bind, checkfirst=True)

