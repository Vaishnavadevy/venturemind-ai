"""Platform-wide announcements created by an administrator."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PlatformAnnouncement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An administrator message shown to a selected VentureMind audience."""

    __tablename__ = "platform_announcements"

    title: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str] = mapped_column(String(24), nullable=False, default="all")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        Index("ix_platform_announcements_active_audience_created", "is_active", "audience", "created_at"),
    )
