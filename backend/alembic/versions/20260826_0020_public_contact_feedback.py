"""Allow contact-page feedback without an account and store contact details.

Revision ID: 20260826_0020
Revises: 20260823_0019
"""

from alembic import op
import sqlalchemy as sa

revision = "20260826_0020"
down_revision = "20260823_0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("feedback"):
        return
    columns = {column["name"] for column in inspector.get_columns("feedback")}
    if "contact_name" not in columns:
        op.add_column("feedback", sa.Column("contact_name", sa.String(length=120), nullable=True))
    if "contact_email" not in columns:
        op.add_column("feedback", sa.Column("contact_email", sa.String(length=320), nullable=True))
    if "user_id" in columns:
        op.alter_column("feedback", "user_id", existing_type=sa.String(length=36), nullable=True)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("feedback"):
        return
    columns = {column["name"] for column in inspector.get_columns("feedback")}
    if "contact_email" in columns:
        op.drop_column("feedback", "contact_email")
    if "contact_name" in columns:
        op.drop_column("feedback", "contact_name")
