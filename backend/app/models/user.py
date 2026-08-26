"""User identity and authentication-token persistence models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import SecurityTokenType, UserRole

if TYPE_CHECKING:
    from app.models.chat import ChatConversation
    from app.models.feedback import Feedback
    from app.models.notification import Notification
    from app.models.project import Project


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An authenticated platform account."""

    __tablename__ = "users"

    # 191 keeps this unique index compatible with older MySQL/MariaDB UTF-8 limits.
    email: Mapped[str] = mapped_column(String(191), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=24), nullable=False, default=UserRole.USER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    security_tokens: Mapped[list["SecurityToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    feedback_entries: Mapped[list["Feedback"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    chat_conversations: Mapped[list["ChatConversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_users_role_active", "role", "is_active"),)


class SecurityToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A hashed, revocable refresh or one-time account security token."""

    __tablename__ = "security_tokens"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_type: Mapped[SecurityTokenType] = mapped_column(
        Enum(SecurityTokenType, native_enum=False, length=32), nullable=False
    )
    # 191 keeps the unique index compatible with older MySQL/MariaDB UTF-8 limits.
    token_hash: Mapped[str] = mapped_column(String(191), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    user: Mapped["User"] = relationship(back_populates="security_tokens")

    __table_args__ = (
        Index("ix_security_tokens_user_type", "user_id", "token_type"),
        Index("ix_security_tokens_expiry", "expires_at"),
    )
