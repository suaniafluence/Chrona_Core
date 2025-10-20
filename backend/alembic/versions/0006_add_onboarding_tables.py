"""add onboarding tables (hr_codes, otp_verifications, onboarding_sessions)

Revision ID: 0006_add_onboarding_tables
Revises: 0005_add_kiosk_api_key
Create Date: 2025-10-20
"""

import sqlalchemy as sa

from alembic import op

revision = "0006_add_onboarding_tables"
down_revision = "0005_add_kiosk_api_key"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create hr_codes table
    op.create_table(
        "hr_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("employee_email", sa.String(length=255), nullable=False),
        sa.Column("employee_name", sa.String(length=255), nullable=True),
        sa.Column("created_by_admin_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("used_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["used_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_hr_codes_code"), "hr_codes", ["code"], unique=False)
    op.create_index(
        op.f("ix_hr_codes_employee_email"),
        "hr_codes",
        ["employee_email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_hr_codes_expires_at"), "hr_codes", ["expires_at"], unique=False
    )
    op.create_index(
        op.f("ix_hr_codes_is_used"), "hr_codes", ["is_used"], unique=False
    )

    # Create otp_verifications table
    op.create_table(
        "otp_verifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("otp_code", sa.String(length=10), nullable=False),
        sa.Column("otp_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_otp_verifications_email"),
        "otp_verifications",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_otp_verifications_created_at"),
        "otp_verifications",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_otp_verifications_expires_at"),
        "otp_verifications",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_otp_verifications_is_verified"),
        "otp_verifications",
        ["is_verified"],
        unique=False,
    )

    # Create onboarding_sessions table
    op.create_table(
        "onboarding_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_token", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hr_code_id", sa.Integer(), nullable=True),
        sa.Column("step", sa.String(length=50), nullable=False, server_default="hr_code"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("device_fingerprint_candidate", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["hr_code_id"], ["hr_codes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token"),
    )
    op.create_index(
        op.f("ix_onboarding_sessions_session_token"),
        "onboarding_sessions",
        ["session_token"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_sessions_email"),
        "onboarding_sessions",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_sessions_expires_at"),
        "onboarding_sessions",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables in reverse order (respect foreign keys)
    op.drop_index(
        op.f("ix_onboarding_sessions_expires_at"), table_name="onboarding_sessions"
    )
    op.drop_index(
        op.f("ix_onboarding_sessions_email"), table_name="onboarding_sessions"
    )
    op.drop_index(
        op.f("ix_onboarding_sessions_session_token"), table_name="onboarding_sessions"
    )
    op.drop_table("onboarding_sessions")

    op.drop_index(
        op.f("ix_otp_verifications_is_verified"), table_name="otp_verifications"
    )
    op.drop_index(
        op.f("ix_otp_verifications_expires_at"), table_name="otp_verifications"
    )
    op.drop_index(
        op.f("ix_otp_verifications_created_at"), table_name="otp_verifications"
    )
    op.drop_index(op.f("ix_otp_verifications_email"), table_name="otp_verifications")
    op.drop_table("otp_verifications")

    op.drop_index(op.f("ix_hr_codes_is_used"), table_name="hr_codes")
    op.drop_index(op.f("ix_hr_codes_expires_at"), table_name="hr_codes")
    op.drop_index(op.f("ix_hr_codes_employee_email"), table_name="hr_codes")
    op.drop_index(op.f("ix_hr_codes_code"), table_name="hr_codes")
    op.drop_table("hr_codes")
