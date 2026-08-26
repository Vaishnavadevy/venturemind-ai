"""Conversation and message history for the contextual AI assistant."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class ChatConversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A named assistant conversation, optionally scoped to a project."""

    __tablename__ = "chat_conversations"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="New conversation")

    user: Mapped["User"] = relationship(back_populates="chat_conversations")
    project: Mapped["Project | None"] = relationship()
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.sequence_number",
    )

    __table_args__ = (Index("ix_chat_conversations_user_created", "user_id", "created_at"),)


class ChatMessage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An immutable user, assistant, or system message."""

    __tablename__ = "chat_messages"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_metadata: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    conversation: Mapped["ChatConversation"] = relationship(back_populates="messages")

    __table_args__ = (
        Index(
            "uq_chat_messages_conversation_sequence",
            "conversation_id",
            "sequence_number",
            unique=True,
        ),
    )
