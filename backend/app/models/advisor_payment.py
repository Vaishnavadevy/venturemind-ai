"""Demonstration payment records for paid advisor consultations.

No money is charged until a real payment provider is configured.
"""

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AdvisorBookingPayment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "advisor_booking_payments"

    booking_request_id: Mapped[str] = mapped_column(ForeignKey("advisor_booking_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    founder_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount_lkr: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    provider: Mapped[str] = mapped_column(String(40), nullable=False, default="demo")
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)

    __table_args__ = (Index("ix_advisor_payment_founder_status", "founder_id", "status"),)
