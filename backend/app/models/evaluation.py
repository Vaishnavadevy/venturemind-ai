"""AI evaluation, normalized scores, and persisted analysis artifacts."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import EvaluationStatus

if TYPE_CHECKING:
    from app.models.project import Project, StartupIdea
    from app.models.report import Report


class Evaluation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One evaluation run for a particular startup-idea version."""

    __tablename__ = "evaluations"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    startup_idea_id: Mapped[str] = mapped_column(
        ForeignKey("startup_ideas.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[EvaluationStatus] = mapped_column(
        Enum(EvaluationStatus, native_enum=False, length=24),
        nullable=False,
        default=EvaluationStatus.QUEUED,
    )
    pipeline_version: Mapped[str] = mapped_column(String(50), nullable=False)
    overall_confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    structured_extraction: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    swot_analysis: Mapped[dict[str, list[str]] | None] = mapped_column(JSON, nullable=True)
    business_model_canvas: Mapped[dict[str, str] | None] = mapped_column(JSON, nullable=True)
    market_analysis: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    competitor_analysis: Mapped[list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    risk_analysis: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    investment_readiness: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    roadmap: Mapped[list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    financial_forecast: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[list[dict[str, str]] | None] = mapped_column(JSON, nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="evaluations")
    startup_idea: Mapped["StartupIdea"] = relationship(back_populates="evaluations")
    scores: Mapped[list["EvaluationScore"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(back_populates="evaluation")

    __table_args__ = (
        Index("ix_evaluations_project_status", "project_id", "status"),
        Index("ix_evaluations_idea_created", "startup_idea_id", "created_at"),
    )


class EvaluationScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single explainable dimension of an evaluation."""

    __tablename__ = "evaluation_scores"

    evaluation_id: Mapped[str] = mapped_column(
        ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    metric_key: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    positive_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    negative_factors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    improvement_suggestions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    factor_breakdown: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    evaluation: Mapped["Evaluation"] = relationship(back_populates="scores")

    __table_args__ = (
        Index("uq_evaluation_scores_evaluation_metric", "evaluation_id", "metric_key", unique=True),
    )
