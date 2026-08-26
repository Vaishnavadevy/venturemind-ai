"""Database-backed educational company-registration guide.

Revision ID: 20260822_0016
Revises: 20260822_0015
"""

from alembic import op
import sqlalchemy as sa


revision = "20260822_0016"
down_revision = "20260822_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_registration_journeys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("startup_profile_id", sa.String(36), sa.ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("mode", sa.String(16), nullable=False, server_default="guide"),
        sa.Column("company_type", sa.String(120), nullable=True),
        sa.Column("proposed_company_name", sa.String(180), nullable=True),
        sa.Column("overall_status", sa.String(32), nullable=False, server_default="not_started"),
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "business_registration_checklist_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("journey_id", sa.String(36), sa.ForeignKey("business_registration_journeys.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_key", sa.String(80), nullable=False),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("official_url", sa.String(600), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="not_started"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("journey_id", "item_key", name="uq_registration_journey_item_key"),
    )
    op.create_index("ix_registration_checklist_journey_step", "business_registration_checklist_items", ["journey_id", "step_number"])


def downgrade() -> None:
    op.drop_index("ix_registration_checklist_journey_step", table_name="business_registration_checklist_items")
    op.drop_table("business_registration_checklist_items")
    op.drop_table("business_registration_journeys")
