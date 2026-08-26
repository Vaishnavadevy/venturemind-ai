"""Generated report metadata."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReportStatus

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation
    from app.models.project import Project


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A generated downloadable evaluation report."""

    __tablename__ = "reports"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    evaluation_id: Mapped[str] = mapped_column(
        ForeignKey("evaluations.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, native_enum=False, length=24),
        nullable=False,
        default=ReportStatus.PENDING,
    )
    storage_key: Mapped[str | None] = mapped_column(String(191), nullable=True, unique=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="reports")
    evaluation: Mapped["Evaluation"] = relationship(back_populates="reports")

    __table_args__ = (Index("ix_reports_project_status", "project_id", "status"),)
