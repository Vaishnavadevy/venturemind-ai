"""Founder-controlled state for data-derived dashboard recommendations."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class SmartRecommendationState(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores acknowledgement/completion without changing the source business data."""

    __tablename__ = "smart_recommendation_states"

    startup_profile_id: Mapped[str] = mapped_column(
        ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False
    )
    recommendation_key: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="open")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("uq_smart_recommendation_profile_key", "startup_profile_id", "recommendation_key", unique=True),
    )
