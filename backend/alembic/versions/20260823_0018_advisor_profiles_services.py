"""advisor profile workspace and service fees

Revision ID: 20260823_0018
Revises: 20260822_0017
"""

from alembic import op
import sqlalchemy as sa

revision = "20260823_0018"
down_revision = "20260822_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("advisor_profiles"):
        columns = {item["name"] for item in inspector.get_columns("advisor_profiles")}
        additions = {
            "qualifications": sa.Text(),
            "registration_details": sa.String(500),
            "membership_plan": sa.String(20),
            "office_address": sa.String(500),
            "service_fees": sa.JSON(),
        }
        for name, column_type in additions.items():
            if name not in columns:
                nullable = name != "membership_plan"
                op.add_column("advisor_profiles", sa.Column(name, column_type, nullable=nullable, server_default="general" if name == "membership_plan" else None))
    if inspector.has_table("advisor_booking_requests"):
        columns = {item["name"] for item in inspector.get_columns("advisor_booking_requests")}
        if "service_name" not in columns:
            op.add_column("advisor_booking_requests", sa.Column("service_name", sa.String(160), nullable=False, server_default="General consultation"))
        if "quoted_fee_lkr" not in columns:
            op.add_column("advisor_booking_requests", sa.Column("quoted_fee_lkr", sa.Numeric(12, 2), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("advisor_booking_requests", "quoted_fee_lkr")
    op.drop_column("advisor_booking_requests", "service_name")
    for column in ["service_fees", "office_address", "membership_plan", "registration_details", "qualifications"]:
        op.drop_column("advisor_profiles", column)
