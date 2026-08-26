"""Create VentureMind's initial normalized schema.

Revision ID: 20260712_0001
Revises:
Create Date: 2026-07-12
"""

import sqlalchemy as sa

from alembic import op

revision = "20260712_0001"
down_revision = None
branch_labels = None
depends_on = None


def id_column() -> sa.Column[str]:
    return sa.Column("id", sa.String(length=36), nullable=False)


def timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        id_column(),
        # 191 keeps this unique index compatible with older MySQL/MariaDB UTF-8 limits.
        sa.Column("email", sa.String(191), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("role", sa.String(24), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_role_active", "users", ["role", "is_active"])
    op.create_table(
        "projects",
        id_column(),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(24), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_projects_owner_status", "projects", ["owner_id", "status"])
    op.create_table(
        "security_tokens",
        id_column(),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("token_type", sa.String(32), nullable=False),
        sa.Column("token_hash", sa.String(191), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime()),
        sa.Column("revoked_at", sa.DateTime()),
        sa.Column("user_agent", sa.String(512)),
        sa.Column("ip_address", sa.String(45)),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_security_tokens_user_type", "security_tokens", ["user_id", "token_type"])
    op.create_index("ix_security_tokens_expiry", "security_tokens", ["expires_at"])
    op.create_table(
        "startup_ideas",
        id_column(),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("startup_name", sa.String(160), nullable=False),
        sa.Column("industry", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("target_audience", sa.Text(), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=False),
        sa.Column("proposed_solution", sa.Text(), nullable=False),
        sa.Column("business_model", sa.Text(), nullable=False),
        sa.Column("revenue_model", sa.Text(), nullable=False),
        sa.Column("development_stage", sa.String(24), nullable=False),
        sa.Column("budget_amount", sa.Numeric(14, 2)),
        sa.Column("budget_currency", sa.String(3)),
        sa.Column("competitors", sa.JSON(), nullable=False),
        sa.Column("additional_notes", sa.Text()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("project_id", "version", name="uq_startup_ideas_project_version"),
    )
    op.create_index("ix_startup_ideas_industry_country", "startup_ideas", ["industry", "country"])
    op.create_table(
        "evaluations",
        id_column(),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("startup_idea_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("pipeline_version", sa.String(50), nullable=False),
        sa.Column("overall_confidence_score", sa.Numeric(5, 2)),
        sa.Column("structured_extraction", sa.JSON()),
        sa.Column("swot_analysis", sa.JSON()),
        sa.Column("business_model_canvas", sa.JSON()),
        sa.Column("market_analysis", sa.JSON()),
        sa.Column("competitor_analysis", sa.JSON()),
        sa.Column("risk_analysis", sa.JSON()),
        sa.Column("investment_readiness", sa.JSON()),
        sa.Column("roadmap", sa.JSON()),
        sa.Column("financial_forecast", sa.JSON()),
        sa.Column("recommendations", sa.JSON()),
        sa.Column("llm_model", sa.String(100)),
        sa.Column("input_tokens", sa.Integer()),
        sa.Column("output_tokens", sa.Integer()),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("failure_reason", sa.Text()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["startup_idea_id"], ["startup_ideas.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_evaluations_project_status", "evaluations", ["project_id", "status"])
    op.create_index("ix_evaluations_idea_created", "evaluations", ["startup_idea_id", "created_at"])
    op.create_table(
        "evaluation_scores",
        id_column(),
        sa.Column("evaluation_id", sa.String(36), nullable=False),
        sa.Column("metric_key", sa.String(64), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("weight", sa.Numeric(5, 4), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("positive_factors", sa.JSON(), nullable=False),
        sa.Column("negative_factors", sa.JSON(), nullable=False),
        sa.Column("improvement_suggestions", sa.JSON(), nullable=False),
        sa.Column("factor_breakdown", sa.JSON()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "evaluation_id", "metric_key", name="uq_evaluation_scores_evaluation_metric"
        ),
    )
    op.create_table(
        "reports",
        id_column(),
        sa.Column("project_id", sa.String(36), nullable=False),
        sa.Column("evaluation_id", sa.String(36)),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("storage_key", sa.String(191)),
        sa.Column("file_name", sa.String(255)),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("file_size_bytes", sa.Integer()),
        sa.Column("generated_at", sa.DateTime()),
        sa.Column("expires_at", sa.DateTime()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_reports_project_status", "reports", ["project_id", "status"])
    op.create_table(
        "feedback",
        id_column(),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer()),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("admin_note", sa.Text()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_feedback_status_created", "feedback", ["status", "created_at"])
    op.create_table(
        "chat_conversations",
        id_column(),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(36)),
        sa.Column("title", sa.String(200), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_chat_conversations_user_created", "chat_conversations", ["user_id", "created_at"]
    )
    op.create_table(
        "chat_messages",
        id_column(),
        sa.Column("conversation_id", sa.String(36), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(100)),
        sa.Column("token_count", sa.Integer()),
        sa.Column("context_metadata", sa.JSON()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "conversation_id", "sequence_number", name="uq_chat_messages_conversation_sequence"
        ),
    )
    op.create_table(
        "notifications",
        id_column(),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("notification_type", sa.String(32), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON()),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("read_at", sa.DateTime()),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_notifications_user_unread_created",
        "notifications",
        ["user_id", "is_read", "created_at"],
    )


def downgrade() -> None:
    for table in [
        "notifications",
        "chat_messages",
        "chat_conversations",
        "feedback",
        "reports",
        "evaluation_scores",
        "evaluations",
        "startup_ideas",
        "security_tokens",
        "projects",
        "users",
    ]:
        op.drop_table(table)
