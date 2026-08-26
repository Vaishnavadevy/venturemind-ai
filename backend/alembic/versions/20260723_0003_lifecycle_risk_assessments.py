"""Add persisted lifecycle startup risk assessments.

Revision ID: 20260723_0003
Revises: 20260722_0002
"""

import sqlalchemy as sa
from alembic import op

revision = "20260723_0003"
down_revision = "20260722_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lifecycle_risk_assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("startup_profile_id", sa.String(36), nullable=False),
        sa.Column("overall_success_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("business_confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("overall_risk_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_level", sa.String(24), nullable=False),
        sa.Column("methodology_version", sa.String(50), nullable=False),
        sa.Column("scorecards", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["startup_profile_id"], ["startup_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_lifecycle_risk_profile_created", "lifecycle_risk_assessments", ["startup_profile_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_lifecycle_risk_profile_created", table_name="lifecycle_risk_assessments")
    op.drop_table("lifecycle_risk_assessments")
