"""human advisor booking requests

Revision ID: 20260731_0006
Revises: 20260724_0005
"""
from alembic import op
import sqlalchemy as sa

revision = "20260731_0006"
down_revision = "20260724_0005"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("advisor_booking_requests", sa.Column("id", sa.String(36), primary_key=True), sa.Column("founder_id", sa.String(36), nullable=False), sa.Column("advisor_id", sa.String(36), nullable=False), sa.Column("consultation_type", sa.String(32), nullable=False), sa.Column("topic", sa.String(160), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.ForeignKeyConstraint(["founder_id"], ["users.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["advisor_id"], ["users.id"], ondelete="CASCADE"))
    op.create_index("ix_advisor_bookings_advisor_status", "advisor_booking_requests", ["advisor_id", "status"])

def downgrade():
    op.drop_index("ix_advisor_bookings_advisor_status", table_name="advisor_booking_requests")
    op.drop_table("advisor_booking_requests")
