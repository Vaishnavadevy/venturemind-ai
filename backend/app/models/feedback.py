"""User feedback persisted for admin review."""

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import FeedbackStatus

if TYPE_CHECKING:
    from app.models.user import User


class Feedback(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Product or evaluation feedback supplied by a user."""

    __tablename__ = "feedback"

    # Contact-page feedback can be submitted before a visitor creates an account.
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(FeedbackStatus, native_enum=False, length=24),
        nullable=False,
        default=FeedbackStatus.OPEN,
    )
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="feedback_entries")

    __table_args__ = (Index("ix_feedback_status_created", "status", "created_at"),)
