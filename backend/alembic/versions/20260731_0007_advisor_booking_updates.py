"""advisor booking workflow fields

Revision ID: 20260731_0007
Revises: 20260731_0006
"""
from alembic import op
import sqlalchemy as sa

revision = "20260731_0007"
down_revision = "20260731_0006"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("advisor_booking_requests", sa.Column("advisor_note", sa.Text(), nullable=True))
    op.add_column("advisor_booking_requests", sa.Column("scheduled_at", sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column("advisor_booking_requests", "scheduled_at")
    op.drop_column("advisor_booking_requests", "advisor_note")
