"""admin content, audit logs and advisor verification

Revision ID: 20260816_0009
Revises: 20260816_0008
"""

from alembic import op
import sqlalchemy as sa

revision = "20260816_0009"
down_revision = "20260816_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("content_items", sa.Column("id", sa.String(36), primary_key=True), sa.Column("content_type", sa.String(40), nullable=False), sa.Column("title", sa.String(220), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("source_url", sa.String(600), nullable=True), sa.Column("image_url", sa.String(600), nullable=True), sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_content_items_type_published_created", "content_items", ["content_type", "is_published", "created_at"])
    op.create_table("audit_logs", sa.Column("id", sa.String(36), primary_key=True), sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("action", sa.String(120), nullable=False), sa.Column("target_type", sa.String(80), nullable=False), sa.Column("target_id", sa.String(36), nullable=True), sa.Column("detail", sa.JSON(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_audit_logs_created_action", "audit_logs", ["created_at", "action"])
    op.create_table("advisor_verification_requests", sa.Column("id", sa.String(36), primary_key=True), sa.Column("applicant_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("requested_role", sa.String(32), nullable=False), sa.Column("document_type", sa.String(32), nullable=False), sa.Column("document_reference", sa.String(120), nullable=False), sa.Column("registration_number", sa.String(120), nullable=True), sa.Column("professional_summary", sa.Text(), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("reviewer_note", sa.Text(), nullable=True), sa.Column("reviewed_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("reviewed_at", sa.DateTime(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_advisor_verification_status_created", "advisor_verification_requests", ["status", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_advisor_verification_status_created", table_name="advisor_verification_requests")
    op.drop_table("advisor_verification_requests")
    op.drop_index("ix_audit_logs_created_action", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_content_items_type_published_created", table_name="content_items")
    op.drop_table("content_items")
