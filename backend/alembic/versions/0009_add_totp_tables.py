"""add_totp_tables

Revision ID: 0009_add_totp_tables
Revises: 0008_add_kiosk_access_control
Create Date: 2025-04-28 00:00:00.000000

Adds TOTP (Time-based One-Time Password) authentication tables:
- totp_secrets: Encrypted TOTP secrets with device binding
- totp_recovery_codes: Single-use recovery codes
- totp_nonce_blacklist: Replay attack protection
- totp_validation_attempts: Rate limiting and monitoring
- totp_lockouts: Account lockout after excessive failures

Compliant with employee and kiosk security specifications.
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0009_add_totp_tables"
down_revision: Union[str, None] = "0008_add_kiosk_access_control"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create totp_secrets table
    op.create_table(
        "totp_secrets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("encrypted_secret", sa.String(), nullable=False),
        sa.Column("encryption_key_id", sa.String(length=100), nullable=False),
        sa.Column("algorithm", sa.String(length=20), nullable=False),
        sa.Column("digits", sa.Integer(), nullable=False),
        sa.Column("period", sa.Integer(), nullable=False),
        sa.Column("provisioning_qr_expires_at", sa.DateTime(), nullable=True),
        sa.Column("is_activated", sa.Boolean(), nullable=False),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("key_rotation_due_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_totp_secrets_user_id"), "totp_secrets", ["user_id"], unique=False)
    op.create_index(op.f("ix_totp_secrets_device_id"), "totp_secrets", ["device_id"], unique=False)
    op.create_index(
        op.f("ix_totp_secrets_provisioning_qr_expires_at"),
        "totp_secrets",
        ["provisioning_qr_expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_secrets_is_activated"),
        "totp_secrets",
        ["is_activated"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_secrets_is_active"), "totp_secrets", ["is_active"], unique=False
    )
    op.create_index(
        op.f("ix_totp_secrets_key_rotation_due_at"),
        "totp_secrets",
        ["key_rotation_due_at"],
        unique=False,
    )

    # Create totp_recovery_codes table
    op.create_table(
        "totp_recovery_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("totp_secret_id", sa.Integer(), nullable=False),
        sa.Column("code_hash", sa.String(), nullable=False),
        sa.Column("code_hint", sa.String(length=10), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("used_from_ip", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["totp_secret_id"],
            ["totp_secrets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_totp_recovery_codes_user_id"),
        "totp_recovery_codes",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_recovery_codes_totp_secret_id"),
        "totp_recovery_codes",
        ["totp_secret_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_recovery_codes_is_used"),
        "totp_recovery_codes",
        ["is_used"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_recovery_codes_expires_at"),
        "totp_recovery_codes",
        ["expires_at"],
        unique=False,
    )

    # Create totp_nonce_blacklist table
    op.create_table(
        "totp_nonce_blacklist",
        sa.Column("nonce", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kiosk_id", sa.Integer(), nullable=True),
        sa.Column("jwt_jti", sa.String(length=255), nullable=False),
        sa.Column("jwt_expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_from_ip", sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kiosk_id"],
            ["kiosks.id"],
        ),
        sa.PrimaryKeyConstraint("nonce"),
    )
    op.create_index(
        op.f("ix_totp_nonce_blacklist_user_id"),
        "totp_nonce_blacklist",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_nonce_blacklist_kiosk_id"),
        "totp_nonce_blacklist",
        ["kiosk_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_nonce_blacklist_jwt_jti"),
        "totp_nonce_blacklist",
        ["jwt_jti"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_nonce_blacklist_jwt_expires_at"),
        "totp_nonce_blacklist",
        ["jwt_expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_nonce_blacklist_consumed_at"),
        "totp_nonce_blacklist",
        ["consumed_at"],
        unique=False,
    )

    # Create totp_validation_attempts table
    op.create_table(
        "totp_validation_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kiosk_id", sa.Integer(), nullable=True),
        sa.Column("is_success", sa.Boolean(), nullable=False),
        sa.Column("failure_reason", sa.String(length=100), nullable=True),
        sa.Column("attempted_at", sa.DateTime(), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("jwt_jti", sa.String(length=255), nullable=True),
        sa.Column("nonce", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kiosk_id"],
            ["kiosks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_totp_validation_attempts_user_id"),
        "totp_validation_attempts",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_validation_attempts_kiosk_id"),
        "totp_validation_attempts",
        ["kiosk_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_validation_attempts_is_success"),
        "totp_validation_attempts",
        ["is_success"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_validation_attempts_attempted_at"),
        "totp_validation_attempts",
        ["attempted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_validation_attempts_ip_address"),
        "totp_validation_attempts",
        ["ip_address"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_validation_attempts_jwt_jti"),
        "totp_validation_attempts",
        ["jwt_jti"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_validation_attempts_nonce"),
        "totp_validation_attempts",
        ["nonce"],
        unique=False,
    )

    # Create totp_lockouts table
    op.create_table(
        "totp_lockouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("locked_at", sa.DateTime(), nullable=False),
        sa.Column("locked_until", sa.DateTime(), nullable=False),
        sa.Column("failed_attempts_count", sa.Integer(), nullable=False),
        sa.Column("trigger_reason", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.Column("released_by", sa.String(length=50), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        op.f("ix_totp_lockouts_user_id"), "totp_lockouts", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_totp_lockouts_locked_until"),
        "totp_lockouts",
        ["locked_until"],
        unique=False,
    )
    op.create_index(
        op.f("ix_totp_lockouts_is_active"), "totp_lockouts", ["is_active"], unique=False
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("totp_lockouts")
    op.drop_table("totp_validation_attempts")
    op.drop_table("totp_nonce_blacklist")
    op.drop_table("totp_recovery_codes")
    op.drop_table("totp_secrets")
