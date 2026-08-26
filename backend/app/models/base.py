"""Shared declarative mixins for persistent entities."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKeyMixin:
    """Use application-generated UUIDs that work consistently with MySQL."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))


class TimestampMixin:
    """Track entity creation and most recent modification times in UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
