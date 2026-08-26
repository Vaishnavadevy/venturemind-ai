"""Lifecycle workspace request and response contracts."""

from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProfileSuggestionRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    category: str = Field(min_length=2, max_length=120)
    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)


class ProfileSuggestions(BaseModel):
    industry: str
    startup_type: str
    target_customers: str
    description: str
    next_question: str


class ProfileSuggestionResponse(BaseModel):
    suggestions: ProfileSuggestions
    mode: str
    notice: str


class StartupProfileUpsert(BaseModel):
    business_name: str = Field(min_length=2, max_length=160)
    category: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=10_000)
    industry: str | None = Field(default=None, max_length=120)
    target_customers: str | None = Field(default=None, max_length=5_000)
    country: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    expected_investment: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    available_budget: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    business_experience: str | None = Field(default=None, max_length=5_000)
    business_goals: str | None = Field(default=None, max_length=5_000)
    business_size: str | None = Field(default=None, max_length=32)
    startup_type: str | None = Field(default=None, max_length=64)
    partner_count: int = Field(default=1, ge=1, le=100)
    expected_employees: int = Field(default=0, ge=0, le=100_000)
    launch_timeline: str | None = Field(default=None, max_length=160)


class StartupProfileResponse(StartupProfileUpsert):
    model_config = ConfigDict(from_attributes=True)
    id: str
    organization_id: str
    status: str


class MilestoneUpdate(BaseModel):
    completed: bool


class LifecycleMilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    milestone_key: str
    title: str
    weight: int
    completed_at: str | None = None


class RiskScorecardResponse(BaseModel):
    key: str
    label: str
    risk_score: float
    reasoning: str
    positive_factors: list[str]
    negative_factors: list[str]
    suggestions: list[str]


class LifecycleRiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    startup_profile_id: str
    overall_success_score: float
    business_confidence_score: float
    overall_risk_score: float
    risk_level: str
    methodology_version: str
    scorecards: list[RiskScorecardResponse]
    recommendations: list[dict[str, str]]
    ai_explanation: dict[str, object] | None = None
