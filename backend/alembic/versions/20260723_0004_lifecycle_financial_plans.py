"""Add saved lifecycle financial plans.

Revision ID: 20260723_0004
Revises: 20260723_0003
"""

import sqlalchemy as sa
from alembic import op

revision = "20260723_0004"
down_revision = "20260723_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lifecycle_financial_plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("startup_profile_id", sa.String(36), nullable=False),
        sa.Column("assumptions", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["startup_profile_id"], ["startup_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_lifecycle_financial_profile_created", "lifecycle_financial_plans", ["startup_profile_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_lifecycle_financial_profile_created", table_name="lifecycle_financial_plans")
    op.drop_table("lifecycle_financial_plans")
