"""Evaluation API contracts."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import EvaluationStatus


class EvaluationScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    metric_key: str
    score: Decimal
    weight: Decimal
    reasoning: str
    positive_factors: list[str]
    negative_factors: list[str]
    improvement_suggestions: list[str]
    factor_breakdown: dict[str, object] | None


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    startup_idea_id: str
    status: EvaluationStatus
    pipeline_version: str
    overall_confidence_score: Decimal | None
    structured_extraction: dict[str, object] | None
    recommendations: list[dict[str, str]] | None
    risk_analysis: dict[str, object] | None
    completed_at: datetime | None
    swot_analysis: dict[str, list[str]] | None
    business_model_canvas: dict[str, str] | None
    market_analysis: dict[str, object] | None
    roadmap: list[dict[str, object]] | None
    scores: list[EvaluationScoreResponse]
