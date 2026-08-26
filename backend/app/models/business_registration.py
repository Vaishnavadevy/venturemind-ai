"""Founder-controlled educational business-registration workflow records."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class BusinessRegistrationJourney(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "business_registration_journeys"

    startup_profile_id: Mapped[str] = mapped_column(ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False, unique=True)
    mode: Mapped[str] = mapped_column(String(16), nullable=False, default="guide")
    company_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    proposed_company_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    overall_status: Mapped[str] = mapped_column(String(32), nullable=False, default="not_started")
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class BusinessRegistrationChecklistItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "business_registration_checklist_items"

    journey_id: Mapped[str] = mapped_column(ForeignKey("business_registration_journeys.id", ondelete="CASCADE"), nullable=False)
    item_key: Mapped[str] = mapped_column(String(80), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    official_url: Mapped[str | None] = mapped_column(String(600), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="not_started")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("uq_registration_journey_item_key", "journey_id", "item_key", unique=True),
        Index("ix_registration_checklist_journey_step", "journey_id", "step_number"),
    )
