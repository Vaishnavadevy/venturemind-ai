"""Add organization-aware startup lifecycle persistence.

Revision ID: 20260722_0002
Revises: 20260712_0001
Create Date: 2026-07-22
"""

import sqlalchemy as sa
from alembic import op

revision = "20260722_0002"
down_revision = "20260712_0001"
branch_labels = None
depends_on = None


def audit_columns():
    return [sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False)]


def upgrade() -> None:
    op.create_table("organizations", sa.Column("id", sa.String(36), primary_key=True), sa.Column("owner_id", sa.String(36), nullable=False), sa.Column("name", sa.String(160), nullable=False), sa.Column("country", sa.String(100)), *audit_columns(), sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"))
    op.create_index("ix_organizations_owner_created", "organizations", ["owner_id", "created_at"])
    op.create_table("organization_members", sa.Column("id", sa.String(36), primary_key=True), sa.Column("organization_id", sa.String(36), nullable=False), sa.Column("user_id", sa.String(36), nullable=False), sa.Column("member_role", sa.String(32), nullable=False), *audit_columns(), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.UniqueConstraint("organization_id", "user_id", name="uq_organization_member"))
    op.create_table("startup_profiles", sa.Column("id", sa.String(36), primary_key=True), sa.Column("organization_id", sa.String(36), nullable=False), sa.Column("created_by_id", sa.String(36), nullable=False), sa.Column("business_name", sa.String(160), nullable=False), sa.Column("category", sa.String(120), nullable=False), sa.Column("industry", sa.String(120)), sa.Column("description", sa.Text(), nullable=False), sa.Column("target_customers", sa.Text()), sa.Column("country", sa.String(100)), sa.Column("district", sa.String(100)), sa.Column("city", sa.String(100)), sa.Column("expected_investment", sa.Numeric(14,2)), sa.Column("available_budget", sa.Numeric(14,2)), sa.Column("business_experience", sa.Text()), sa.Column("business_goals", sa.Text()), sa.Column("business_size", sa.String(32)), sa.Column("startup_type", sa.String(64)), sa.Column("partner_count", sa.Integer(), nullable=False), sa.Column("expected_employees", sa.Integer(), nullable=False), sa.Column("launch_timeline", sa.String(160)), sa.Column("status", sa.String(24), nullable=False), *audit_columns(), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"))
    op.create_index("ix_startup_profiles_organization_status", "startup_profiles", ["organization_id", "status"])
    op.create_table("lifecycle_milestones", sa.Column("id", sa.String(36), primary_key=True), sa.Column("startup_profile_id", sa.String(36), nullable=False), sa.Column("milestone_key", sa.String(64), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("weight", sa.Integer(), nullable=False), sa.Column("completed_at", sa.DateTime()), *audit_columns(), sa.ForeignKeyConstraint(["startup_profile_id"], ["startup_profiles.id"], ondelete="CASCADE"), sa.UniqueConstraint("startup_profile_id", "milestone_key", name="uq_lifecycle_profile_key"))


def downgrade() -> None:
    op.drop_table("lifecycle_milestones")
    op.drop_table("startup_profiles")
    op.drop_table("organization_members")
    op.drop_table("organizations")
