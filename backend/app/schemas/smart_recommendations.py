"""Contracts for the data-derived Founder Smart Recommendations component."""

from datetime import datetime

from pydantic import BaseModel


class SmartRecommendationResponse(BaseModel):
    id: str | None = None
    key: str
    title: str
    reason: str
    priority: str
    related_module: str
    action_label: str
    action_path: str
    status: str
    completed_at: datetime | None = None


class SmartRecommendationSnapshot(BaseModel):
    startup_profile_id: str | None = None
    generated_from: list[str]
    recommendations: list[SmartRecommendationResponse]


class SmartRecommendationStatusUpdate(BaseModel):
    completed: bool
