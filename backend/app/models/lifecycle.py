"""Organization, startup profile, and lifecycle progress persistence models."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (Index("ix_organizations_owner_created", "owner_id", "created_at"),)


class OrganizationMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organization_members"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    member_role: Mapped[str] = mapped_column(String(32), nullable=False, default="founder")

    __table_args__ = (Index("uq_organization_member", "organization_id", "user_id", unique=True),)


class StartupProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "startup_profiles"

    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_customers: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expected_investment: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    available_budget: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    business_experience: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_size: Mapped[str | None] = mapped_column(String(32), nullable=True)
    startup_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    partner_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    expected_employees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    launch_timeline: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft")

    __table_args__ = (Index("ix_startup_profiles_organization_status", "organization_id", "status"),)


class LifecycleMilestone(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lifecycle_milestones"

    startup_profile_id: Mapped[str] = mapped_column(ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False)
    milestone_key: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (Index("uq_lifecycle_profile_key", "startup_profile_id", "milestone_key", unique=True),)


class LifecycleRiskAssessment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A persisted, explainable risk assessment for one startup profile."""

    __tablename__ = "lifecycle_risk_assessments"

    startup_profile_id: Mapped[str] = mapped_column(ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False)
    overall_success_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    business_confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    overall_risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(24), nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(50), nullable=False)
    scorecards: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    recommendations: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False)
    ai_explanation: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (Index("ix_lifecycle_risk_profile_created", "startup_profile_id", "created_at"),)


class LifecycleFinancialPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Saved investment and unit-economics scenario for a startup profile."""

    __tablename__ = "lifecycle_financial_plans"

    startup_profile_id: Mapped[str] = mapped_column(ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False)
    assumptions: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    results: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    __table_args__ = (Index("ix_lifecycle_financial_profile_created", "startup_profile_id", "created_at"),)
