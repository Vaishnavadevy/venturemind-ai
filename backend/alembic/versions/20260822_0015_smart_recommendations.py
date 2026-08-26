"""Founder smart recommendation acknowledgement state.

Revision ID: 20260822_0015
Revises: 20260817_0014
"""

from alembic import op
import sqlalchemy as sa


revision = "20260822_0015"
down_revision = "20260817_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "smart_recommendation_states",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("startup_profile_id", sa.String(36), sa.ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_key", sa.String(80), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="open"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("startup_profile_id", "recommendation_key", name="uq_smart_recommendation_profile_key"),
    )


def downgrade() -> None:
    op.drop_table("smart_recommendation_states")
