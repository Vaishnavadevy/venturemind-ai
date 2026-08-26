"""soft archive user accounts

Revision ID: 20260816_0012
Revises: 20260816_0011
"""
from alembic import op
import sqlalchemy as sa

revision = "20260816_0012"
down_revision = "20260816_0011"
branch_labels = None
depends_on = None

def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "is_archived" not in columns:
        op.execute("ALTER TABLE users ADD COLUMN is_archived BOOLEAN NOT NULL DEFAULT FALSE")
    if "archived_at" not in columns:
        op.execute("ALTER TABLE users ADD COLUMN archived_at DATETIME NULL")

def downgrade() -> None:
    op.drop_column("users", "archived_at")
    op.drop_column("users", "is_archived")
