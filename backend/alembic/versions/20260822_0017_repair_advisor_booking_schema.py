"""repair advisor booking structures for upgraded local databases

Revision ID: 20260822_0017
Revises: 20260822_0016
"""

from alembic import op
import sqlalchemy as sa


revision = "20260822_0017"
down_revision = "20260822_0016"
branch_labels = None
depends_on = None


def _column_names(bind: sa.engine.Connection, table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(bind).get_columns(table_name)}


def upgrade() -> None:
    """Make old local MySQL databases compatible without dropping data."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("advisor_availability_slots"):
        op.create_table(
            "advisor_availability_slots",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("advisor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("starts_at", sa.DateTime(), nullable=False),
            sa.Column("ends_at", sa.DateTime(), nullable=False),
            sa.Column("consultation_type", sa.String(32), nullable=False, server_default="online"),
            sa.Column("is_booked", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_advisor_slots_advisor_start", "advisor_availability_slots", ["advisor_id", "starts_at"])

    if inspector.has_table("advisor_booking_requests"):
        columns = _column_names(bind, "advisor_booking_requests")
        if "advisor_note" not in columns:
            op.add_column("advisor_booking_requests", sa.Column("advisor_note", sa.Text(), nullable=True))
        if "scheduled_at" not in columns:
            op.add_column("advisor_booking_requests", sa.Column("scheduled_at", sa.DateTime(), nullable=True))
        if "availability_slot_id" not in columns:
            op.add_column("advisor_booking_requests", sa.Column("availability_slot_id", sa.String(36), nullable=True))
        if "meeting_url" not in columns:
            op.add_column("advisor_booking_requests", sa.Column("meeting_url", sa.String(600), nullable=True))

    inspector = sa.inspect(bind)
    if not inspector.has_table("advisor_booking_messages"):
        op.create_table("advisor_booking_messages", sa.Column("id", sa.String(36), primary_key=True), sa.Column("booking_request_id", sa.String(36), nullable=False), sa.Column("sender_id", sa.String(36), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index("ix_booking_messages_booking_created", "advisor_booking_messages", ["booking_request_id", "created_at"])
    if not inspector.has_table("advisor_document_requests"):
        op.create_table("advisor_document_requests", sa.Column("id", sa.String(36), primary_key=True), sa.Column("booking_request_id", sa.String(36), nullable=False), sa.Column("advisor_id", sa.String(36), nullable=False), sa.Column("founder_id", sa.String(36), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("instructions", sa.Text(), nullable=True), sa.Column("status", sa.String(24), nullable=False, server_default="requested"), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index("ix_document_requests_founder_status", "advisor_document_requests", ["founder_id", "status"])
    if not inspector.has_table("advisor_shared_documents"):
        op.create_table("advisor_shared_documents", sa.Column("id", sa.String(36), primary_key=True), sa.Column("document_request_id", sa.String(36), nullable=False), sa.Column("founder_id", sa.String(36), nullable=False), sa.Column("storage_key", sa.String(191), nullable=False, unique=True), sa.Column("original_name", sa.String(255), nullable=False), sa.Column("content_type", sa.String(120), nullable=False), sa.Column("size_bytes", sa.Integer(), nullable=False), sa.Column("checksum", sa.String(64), nullable=False), sa.Column("reviewed", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index("ix_shared_documents_request", "advisor_shared_documents", ["document_request_id"])
    if not inspector.has_table("advisor_booking_reminders"):
        op.create_table("advisor_booking_reminders", sa.Column("id", sa.String(36), primary_key=True), sa.Column("booking_request_id", sa.String(36), nullable=False), sa.Column("reminder_kind", sa.String(12), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.UniqueConstraint("booking_request_id", "reminder_kind", name="uq_booking_reminder_kind"))


def downgrade() -> None:
    # This migration only repairs historical local databases; it intentionally preserves data.
    pass
