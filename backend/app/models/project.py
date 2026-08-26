"""Project and submitted startup-idea models."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DevelopmentStage, ProjectStatus

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation
    from app.models.project import Project
    from app.models.report import Report
    from app.models.user import User


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A user-owned container for a startup idea and its outputs."""

    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, native_enum=False, length=24),
        nullable=False,
        default=ProjectStatus.DRAFT,
    )

    owner: Mapped["User"] = relationship(back_populates="projects")
    startup_ideas: Mapped[list["StartupIdea"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_projects_owner_status", "owner_id", "status"),)


class StartupIdea(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Versionable raw startup submission plus structured business inputs."""

    __tablename__ = "startup_ideas"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    startup_name: Mapped[str] = mapped_column(String(160), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_solution: Mapped[str] = mapped_column(Text, nullable=False)
    business_model: Mapped[str] = mapped_column(Text, nullable=False)
    revenue_model: Mapped[str] = mapped_column(Text, nullable=False)
    development_stage: Mapped[DevelopmentStage] = mapped_column(
        Enum(DevelopmentStage, native_enum=False, length=24),
        nullable=False,
        default=DevelopmentStage.IDEA,
    )
    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    budget_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    competitors: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False, default=list)
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="startup_ideas")
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="startup_idea", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("uq_startup_ideas_project_version", "project_id", "version", unique=True),
        Index("ix_startup_ideas_industry_country", "industry", "country"),
    )
