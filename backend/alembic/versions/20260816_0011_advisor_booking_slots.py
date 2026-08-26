"""advisor availability slots and consultation meeting links

Revision ID: 20260816_0011
Revises: 20260816_0010
"""

from alembic import op
import sqlalchemy as sa

revision = "20260816_0011"
down_revision = "20260816_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not sa.inspect(op.get_bind()).has_table("advisor_availability_slots"):
        op.create_table("advisor_availability_slots", sa.Column("id", sa.String(36), primary_key=True), sa.Column("advisor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("starts_at", sa.DateTime(), nullable=False), sa.Column("ends_at", sa.DateTime(), nullable=False), sa.Column("consultation_type", sa.String(32), nullable=False), sa.Column("is_booked", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index("ix_advisor_slots_advisor_start", "advisor_availability_slots", ["advisor_id", "starts_at"])
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("advisor_booking_requests")}
    if "availability_slot_id" not in columns:
        op.execute("ALTER TABLE advisor_booking_requests ADD COLUMN availability_slot_id VARCHAR(36) NULL")
    if "meeting_url" not in columns:
        op.execute("ALTER TABLE advisor_booking_requests ADD COLUMN meeting_url VARCHAR(600) NULL")


def downgrade() -> None:
    op.drop_column("advisor_booking_requests", "meeting_url")
    op.drop_column("advisor_booking_requests", "availability_slot_id")
    op.drop_index("ix_advisor_slots_advisor_start", table_name="advisor_availability_slots")
    op.drop_table("advisor_availability_slots")
