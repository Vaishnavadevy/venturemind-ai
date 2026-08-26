"""Persistent administration models for content, audit evidence, and advisor verification."""

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ContentItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "content_items"

    content_type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (Index("ix_content_items_type_published_created", "content_type", "is_published", "created_at"),)


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    detail: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (Index("ix_audit_logs_created_action", "created_at", "action"),)


class AdvisorVerificationRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "advisor_verification_requests"

    applicant_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    requested_role: Mapped[str] = mapped_column(String(32), nullable=False, default="legal_advisor")
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    document_reference: Mapped[str] = mapped_column(String(120), nullable=False)
    registration_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    professional_summary: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialisation: Mapped[str | None] = mapped_column(String(500), nullable=True)
    languages: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    consultation_fee: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    availability: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    professional_body: Mapped[str | None] = mapped_column(String(220), nullable=True)
    privacy_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    retention_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    retention_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    licence_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    professional_body_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    credential_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    reviewed_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (Index("ix_advisor_verification_status_created", "status", "created_at"),)


class AdvisorVerificationDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Private encrypted document metadata. The encrypted bytes never receive a public URL."""

    __tablename__ = "advisor_verification_documents"

    verification_request_id: Mapped[str] = mapped_column(ForeignKey("advisor_verification_requests.id", ondelete="CASCADE"), nullable=False)
    # 191 keeps a unique utf8mb4 index compatible with legacy WAMP/MyISAM.
    storage_key: Mapped[str] = mapped_column(String(191), nullable=False, unique=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    retention_until: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (Index("ix_advisor_documents_request", "verification_request_id"),)


class AdvisorProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Public directory details copied from an approved verification application."""

    __tablename__ = "advisor_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    photo_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialisation: Mapped[str] = mapped_column(String(500), nullable=False)
    languages: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    consultation_fee: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    availability: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    professional_body: Mapped[str | None] = mapped_column(String(220), nullable=True)
    credential_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    qualifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    registration_details: Mapped[str | None] = mapped_column(String(500), nullable=True)
    membership_plan: Mapped[str] = mapped_column(String(20), nullable=False, default="general")
    office_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    service_fees: Mapped[list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
