"""advisor consultation payment records

Revision ID: 20260817_0013
Revises: 20260816_0012
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_0013"
down_revision = "20260816_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("advisor_booking_payments", sa.Column("id", sa.String(36), primary_key=True), sa.Column("booking_request_id", sa.String(36), sa.ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False, unique=True), sa.Column("founder_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("amount_lkr", sa.Numeric(12, 2), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="pending"), sa.Column("provider", sa.String(40), nullable=False, server_default="demo"), sa.Column("reference", sa.String(120), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_advisor_payment_founder_status", "advisor_booking_payments", ["founder_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_advisor_payment_founder_status", table_name="advisor_booking_payments")
    op.drop_table("advisor_booking_payments")
