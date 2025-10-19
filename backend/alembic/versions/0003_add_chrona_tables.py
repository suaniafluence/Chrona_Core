"""add devices kiosks punches token_tracking audit_logs tables

Revision ID: 0003_add_chrona_tables
Revises: 0002_auth_fields
Create Date: 2025-10-19
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_add_chrona_tables"
down_revision = "0002_auth_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename user table to users for consistency
    op.rename_table("user", "users")

    # Create kiosks table (no dependencies)
    op.create_table(
        "kiosks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kiosk_name", sa.String(length=100), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("device_fingerprint", sa.String(length=255), nullable=False),
        sa.Column("public_key", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kiosk_name"),
        sa.UniqueConstraint("device_fingerprint"),
    )
    op.create_index(
        op.f("ix_kiosks_kiosk_name"), "kiosks", ["kiosk_name"], unique=False
    )
    op.create_index(
        op.f("ix_kiosks_device_fingerprint"),
        "kiosks",
        ["device_fingerprint"],
        unique=False,
    )
    op.create_index(op.f("ix_kiosks_is_active"), "kiosks", ["is_active"], unique=False)

    # Create devices table (depends on users)
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_fingerprint", sa.String(length=255), nullable=False),
        sa.Column("device_name", sa.String(length=100), nullable=False),
        sa.Column("attestation_data", sa.String(), nullable=True),
        sa.Column("registered_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_fingerprint"),
    )
    op.create_index(op.f("ix_devices_user_id"), "devices", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_devices_device_fingerprint"),
        "devices",
        ["device_fingerprint"],
        unique=False,
    )
    op.create_index(
        op.f("ix_devices_is_revoked"), "devices", ["is_revoked"], unique=False
    )

    # Create punches table (depends on users, devices, kiosks)
    op.create_table(
        "punches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("kiosk_id", sa.Integer(), nullable=False),
        sa.Column("punch_type", sa.String(length=20), nullable=False),
        sa.Column("punched_at", sa.DateTime(), nullable=False),
        sa.Column("jwt_jti", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.ForeignKeyConstraint(["kiosk_id"], ["kiosks.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jwt_jti"),
    )
    op.create_index(op.f("ix_punches_user_id"), "punches", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_punches_device_id"), "punches", ["device_id"], unique=False
    )
    op.create_index(
        op.f("ix_punches_kiosk_id"), "punches", ["kiosk_id"], unique=False
    )
    op.create_index(
        op.f("ix_punches_punched_at"), "punches", ["punched_at"], unique=False
    )

    # Create token_tracking table (depends on users, devices, kiosks)
    op.create_table(
        "token_tracking",
        sa.Column("jti", sa.String(length=255), nullable=False),
        sa.Column("nonce", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("consumed_by_kiosk_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.ForeignKeyConstraint(["consumed_by_kiosk_id"], ["kiosks.id"]),
        sa.PrimaryKeyConstraint("jti"),
    )
    op.create_index(
        op.f("ix_token_tracking_nonce"), "token_tracking", ["nonce"], unique=False
    )
    op.create_index(
        op.f("ix_token_tracking_user_id"), "token_tracking", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_token_tracking_device_id"),
        "token_tracking",
        ["device_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_token_tracking_expires_at"),
        "token_tracking",
        ["expires_at"],
        unique=False,
    )

    # Create audit_logs table (depends on users, devices, kiosks)
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("kiosk_id", sa.Integer(), nullable=True),
        sa.Column("event_data", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.ForeignKeyConstraint(["kiosk_id"], ["kiosks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_logs_event_type"), "audit_logs", ["event_type"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_device_id"), "audit_logs", ["device_id"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_kiosk_id"), "audit_logs", ["kiosk_id"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False
    )


def downgrade() -> None:
    # Drop tables in reverse order (respect foreign keys)
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_kiosk_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_device_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_event_type"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_token_tracking_expires_at"), table_name="token_tracking")
    op.drop_index(op.f("ix_token_tracking_device_id"), table_name="token_tracking")
    op.drop_index(op.f("ix_token_tracking_user_id"), table_name="token_tracking")
    op.drop_index(op.f("ix_token_tracking_nonce"), table_name="token_tracking")
    op.drop_table("token_tracking")

    op.drop_index(op.f("ix_punches_punched_at"), table_name="punches")
    op.drop_index(op.f("ix_punches_kiosk_id"), table_name="punches")
    op.drop_index(op.f("ix_punches_device_id"), table_name="punches")
    op.drop_index(op.f("ix_punches_user_id"), table_name="punches")
    op.drop_table("punches")

    op.drop_index(op.f("ix_devices_is_revoked"), table_name="devices")
    op.drop_index(op.f("ix_devices_device_fingerprint"), table_name="devices")
    op.drop_index(op.f("ix_devices_user_id"), table_name="devices")
    op.drop_table("devices")

    op.drop_index(op.f("ix_kiosks_is_active"), table_name="kiosks")
    op.drop_index(op.f("ix_kiosks_device_fingerprint"), table_name="kiosks")
    op.drop_index(op.f("ix_kiosks_kiosk_name"), table_name="kiosks")
    op.drop_table("kiosks")

    # Rename users back to user
    op.rename_table("users", "user")
