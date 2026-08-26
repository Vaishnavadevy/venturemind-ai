"""Human advisor consultation requests."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AdvisorBookingRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "advisor_booking_requests"

    founder_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    advisor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consultation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    topic: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    advisor_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    availability_slot_id: Mapped[str | None] = mapped_column(ForeignKey("advisor_availability_slots.id", ondelete="SET NULL"), nullable=True)
    meeting_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    service_name: Mapped[str] = mapped_column(String(160), nullable=False, default="General consultation")
    quoted_fee_lkr: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    __table_args__ = (Index("ix_advisor_bookings_advisor_status", "advisor_id", "status"),)


class AdvisorAvailabilitySlot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "advisor_availability_slots"

    advisor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    consultation_type: Mapped[str] = mapped_column(String(32), nullable=False, default="online")
    is_booked: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (Index("ix_advisor_slots_advisor_start", "advisor_id", "starts_at"),)


class AdvisorBookingMessage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Private conversation entries scoped to one consultation booking."""

    __tablename__ = "advisor_booking_messages"

    booking_request_id: Mapped[str] = mapped_column(ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (Index("ix_booking_messages_booking_created", "booking_request_id", "created_at"),)


class AdvisorDocumentRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A document an advisor asks a founder to share for a booking."""

    __tablename__ = "advisor_document_requests"

    booking_request_id: Mapped[str] = mapped_column(ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False)
    advisor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    founder_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="requested")

    __table_args__ = (Index("ix_document_requests_founder_status", "founder_id", "status"),)


class AdvisorSharedDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Encrypted founder document metadata. No public document URL is stored."""

    __tablename__ = "advisor_shared_documents"

    document_request_id: Mapped[str] = mapped_column(ForeignKey("advisor_document_requests.id", ondelete="CASCADE"), nullable=False)
    founder_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # 191 keeps a unique utf8mb4 index compatible with legacy WAMP/MyISAM.
    storage_key: Mapped[str] = mapped_column(String(191), nullable=False, unique=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (Index("ix_shared_documents_request", "document_request_id"),)


class AdvisorBookingReminder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Deduplicates scheduled in-app appointment reminders."""

    __tablename__ = "advisor_booking_reminders"

    booking_request_id: Mapped[str] = mapped_column(ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False)
    reminder_kind: Mapped[str] = mapped_column(String(12), nullable=False)

    __table_args__ = (UniqueConstraint("booking_request_id", "reminder_kind", name="uq_booking_reminder_kind"),)
