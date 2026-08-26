"""Read models for the authenticated founder dashboard."""

from datetime import datetime

from pydantic import BaseModel


class DashboardMetric(BaseModel):
    label: str
    value: str
    detail: str


class DashboardProject(BaseModel):
    id: str
    name: str
    industry: str
    stage: str
    status: str
    score: float | None
    evaluation_id: str | None
    updated_at: datetime


class DashboardScore(BaseModel):
    metric: str
    score: float


class DashboardRisk(BaseModel):
    label: str
    level: str
    score: float
    detail: str


class DashboardReport(BaseModel):
    id: str
    name: str
    project_id: str
    evaluation_id: str | None
    generated_at: datetime | None
    status: str


class DashboardJourney(BaseModel):
    """Persisted lifecycle state used to guide the founder through the workspace."""

    profile_complete: bool = False
    risk_complete: bool = False
    financial_plan_complete: bool = False
    requirements_complete: bool = False
    profile_updated_at: datetime | None = None
    profile_id: str | None = None
    project_name: str | None = None
    profile_completion_percentage: int = 0
    risk_score: float | None = None
    monthly_profit: float | None = None
    cash_runway_months: float | None = None
    break_even_months: float | None = None
    registration_progress_percentage: int = 0
    registration_status: str | None = None


class DashboardSnapshot(BaseModel):
    metrics: list[DashboardMetric]
    projects: list[DashboardProject]
    latest_project: DashboardProject | None
    score_breakdown: list[DashboardScore]
    trend: list[DashboardScore]
    risks: list[DashboardRisk]
    reports: list[DashboardReport]
    journey: DashboardJourney = DashboardJourney()
