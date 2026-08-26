"""advisor profiles, private document metadata and review checklist

Revision ID: 20260816_0010
Revises: 20260816_0009
"""

from alembic import op
import sqlalchemy as sa

revision = "20260816_0010"
down_revision = "20260816_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    # WAMP/MariaDB installations used for the local project may not support
    # ``ADD COLUMN IF NOT EXISTS``. Inspect first so the migration is both
    # repeatable and compatible with those versions.
    existing_columns = {column["name"] for column in inspector.get_columns("advisor_verification_requests")}
    required_columns = {
        "photo_url": "VARCHAR(600) NULL",
        "bio": "TEXT NULL",
        "specialisation": "VARCHAR(500) NULL",
        "languages": "JSON NULL",
        "consultation_fee": "NUMERIC(12,2) NULL",
        "availability": "JSON NULL",
        "professional_body": "VARCHAR(220) NULL",
        "privacy_consent": "BOOLEAN NOT NULL DEFAULT FALSE",
        "retention_accepted": "BOOLEAN NOT NULL DEFAULT FALSE",
        "retention_until": "DATE NULL",
        "licence_valid": "BOOLEAN NULL",
        "professional_body_verified": "BOOLEAN NULL",
        "credential_expiry": "DATE NULL",
    }
    for name, definition in required_columns.items():
        if name not in existing_columns:
            op.execute(f"ALTER TABLE advisor_verification_requests ADD COLUMN {name} {definition}")
    if not inspector.has_table("advisor_verification_documents"):
        op.create_table("advisor_verification_documents", sa.Column("id", sa.String(36), primary_key=True), sa.Column("verification_request_id", sa.String(36), sa.ForeignKey("advisor_verification_requests.id", ondelete="CASCADE"), nullable=False), sa.Column("storage_key", sa.String(191), nullable=False, unique=True), sa.Column("original_name", sa.String(255), nullable=False), sa.Column("content_type", sa.String(120), nullable=False), sa.Column("size_bytes", sa.Integer(), nullable=False), sa.Column("checksum", sa.String(64), nullable=False), sa.Column("retention_until", sa.Date(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.create_index("ix_advisor_documents_request", "advisor_verification_documents", ["verification_request_id"])
    if not inspector.has_table("advisor_profiles"):
        op.create_table("advisor_profiles", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True), sa.Column("photo_url", sa.String(600), nullable=True), sa.Column("bio", sa.Text(), nullable=True), sa.Column("specialisation", sa.String(500), nullable=False), sa.Column("languages", sa.JSON(), nullable=True), sa.Column("consultation_fee", sa.Numeric(12, 2), nullable=True), sa.Column("availability", sa.JSON(), nullable=True), sa.Column("professional_body", sa.String(220), nullable=True), sa.Column("credential_expiry", sa.Date(), nullable=True), sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_table("advisor_profiles")
    op.drop_index("ix_advisor_documents_request", table_name="advisor_verification_documents")
    op.drop_table("advisor_verification_documents")
    for column in ["credential_expiry", "professional_body_verified", "licence_valid", "retention_until", "retention_accepted", "privacy_consent", "professional_body", "availability", "consultation_fee", "languages", "specialisation", "bio", "photo_url"]:
        op.drop_column("advisor_verification_requests", column)
