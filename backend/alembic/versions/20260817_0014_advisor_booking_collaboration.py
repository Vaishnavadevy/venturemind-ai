"""advisor consultation messages, documents, and reminders

Revision ID: 20260817_0014
Revises: 20260817_0013
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_0014"
down_revision = "20260817_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Early development builds created some advisor tables manually.  Inspecting
    # first makes this migration safe for those existing local databases while
    # retaining normal first-install behaviour.
    tables = set(sa.inspect(op.get_bind()).get_table_names())

    if "advisor_booking_messages" not in tables:
        op.create_table("advisor_booking_messages", sa.Column("id", sa.String(36), primary_key=True), sa.Column("booking_request_id", sa.String(36), sa.ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False), sa.Column("sender_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    if "advisor_document_requests" not in tables:
        op.create_table("advisor_document_requests", sa.Column("id", sa.String(36), primary_key=True), sa.Column("booking_request_id", sa.String(36), sa.ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False), sa.Column("advisor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("founder_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("instructions", sa.Text(), nullable=True), sa.Column("status", sa.String(24), nullable=False, server_default="requested"), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    if "advisor_shared_documents" not in tables:
        op.create_table("advisor_shared_documents", sa.Column("id", sa.String(36), primary_key=True), sa.Column("document_request_id", sa.String(36), sa.ForeignKey("advisor_document_requests.id", ondelete="CASCADE"), nullable=False), sa.Column("founder_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("storage_key", sa.String(191), nullable=False, unique=True), sa.Column("original_name", sa.String(255), nullable=False), sa.Column("content_type", sa.String(120), nullable=False), sa.Column("size_bytes", sa.Integer(), nullable=False), sa.Column("checksum", sa.String(64), nullable=False), sa.Column("reviewed", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    if "advisor_booking_reminders" not in tables:
        op.create_table("advisor_booking_reminders", sa.Column("id", sa.String(36), primary_key=True), sa.Column("booking_request_id", sa.String(36), sa.ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False), sa.Column("reminder_kind", sa.String(12), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.UniqueConstraint("booking_request_id", "reminder_kind", name="uq_booking_reminder_kind"))

    indexes = {table: {item["name"] for item in sa.inspect(op.get_bind()).get_indexes(table)} for table in ("advisor_booking_messages", "advisor_document_requests", "advisor_shared_documents")}
    if "ix_booking_messages_booking_created" not in indexes["advisor_booking_messages"]:
        op.create_index("ix_booking_messages_booking_created", "advisor_booking_messages", ["booking_request_id", "created_at"])
    if "ix_document_requests_founder_status" not in indexes["advisor_document_requests"]:
        op.create_index("ix_document_requests_founder_status", "advisor_document_requests", ["founder_id", "status"])
    if "ix_shared_documents_request" not in indexes["advisor_shared_documents"]:
        op.create_index("ix_shared_documents_request", "advisor_shared_documents", ["document_request_id"])


def downgrade() -> None:
    op.drop_table("advisor_booking_reminders")
    op.drop_index("ix_shared_documents_request", table_name="advisor_shared_documents")
    op.drop_table("advisor_shared_documents")
    op.drop_index("ix_document_requests_founder_status", table_name="advisor_document_requests")
    op.drop_table("advisor_document_requests")
    op.drop_index("ix_booking_messages_booking_created", table_name="advisor_booking_messages")
    op.drop_table("advisor_booking_messages")
