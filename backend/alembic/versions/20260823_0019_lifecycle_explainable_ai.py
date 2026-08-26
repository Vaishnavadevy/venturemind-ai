"""persist optional local-AI explanations for lifecycle risk assessments

Revision ID: 20260823_0019
Revises: 20260823_0018
"""

from alembic import op
import sqlalchemy as sa

revision = "20260823_0019"
down_revision = "20260823_0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("lifecycle_risk_assessments"):
        columns = {column["name"] for column in inspector.get_columns("lifecycle_risk_assessments")}
        if "ai_explanation" not in columns:
            op.add_column("lifecycle_risk_assessments", sa.Column("ai_explanation", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("lifecycle_risk_assessments", "ai_explanation")
