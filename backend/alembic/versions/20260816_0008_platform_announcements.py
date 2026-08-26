"""platform announcements

Revision ID: 20260816_0008
Revises: 20260731_0007
"""

from alembic import op
import sqlalchemy as sa

revision = "20260816_0008"
down_revision = "20260731_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_announcements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("audience", sa.String(length=24), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_platform_announcements_active_audience_created", "platform_announcements", ["is_active", "audience", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_platform_announcements_active_audience_created", table_name="platform_announcements")
    op.drop_table("platform_announcements")
