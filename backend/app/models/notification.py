"""In-app notification model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import NotificationType

if TYPE_CHECKING:
    from app.models.user import User


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A user-facing notification with optional deep-link metadata."""

    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, native_enum=False, length=32), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user_unread_created", "user_id", "is_read", "created_at"),
    )
