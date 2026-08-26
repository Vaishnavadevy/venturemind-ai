"""Request and response contracts for startup project submission."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DevelopmentStage, ProjectStatus


class CreateProjectRequest(BaseModel):
    startup_name: str = Field(min_length=2, max_length=160)
    industry: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    target_audience: str = Field(min_length=20, max_length=5_000)
    problem_statement: str = Field(min_length=30, max_length=10_000)
    proposed_solution: str = Field(min_length=30, max_length=10_000)
    business_model: str = Field(min_length=10, max_length=5_000)
    revenue_model: str = Field(min_length=10, max_length=5_000)
    development_stage: DevelopmentStage
    budget_amount: Decimal | None = Field(default=None, ge=0, max_digits=14, decimal_places=2)
    budget_currency: str | None = Field(default=None, min_length=3, max_length=3)
    competitors: list[str] = Field(default_factory=list, max_length=50)
    additional_notes: str | None = Field(default=None, max_length=10_000)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: ProjectStatus


class StartupIdeaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    version: int
    startup_name: str


class ProjectSubmissionResponse(BaseModel):
    project: ProjectResponse
    startup_idea: StartupIdeaResponse
    evaluation_id: str
