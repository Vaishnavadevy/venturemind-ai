"""Contracts for administrator-only management and analytics endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import FeedbackStatus, UserRole


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_email_verified: bool
    created_at: datetime


class UpdateUserStatusRequest(BaseModel):
    is_active: bool | None = None
    role: UserRole | None = None
    is_email_verified: bool | None = None

    @model_validator(mode="after")
    def requires_change(self) -> "UpdateUserStatusRequest":
        if self.is_active is None and self.role is None and self.is_email_verified is None:
            raise ValueError("Provide at least one user change.")
        return self


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    contact_name: str | None = None
    contact_email: str | None = None
    category: str
    message: str
    rating: int | None
    status: FeedbackStatus
    admin_note: str | None
    created_at: datetime


class UpdateFeedbackRequest(BaseModel):
    status: FeedbackStatus
    admin_note: str | None = None


class AnalyticsResponse(BaseModel):
    total_users: int
    active_users: int
    total_projects: int
    total_evaluations: int
    completed_evaluations: int
    total_reports: int
    open_feedback: int
    ai_input_tokens: int
    ai_output_tokens: int


class TrendPoint(BaseModel):
    label: str
    users: int = 0
    projects: int = 0
    evaluations: int = 0


class DistributionItem(BaseModel):
    label: str
    value: int


class AdminAlertResponse(BaseModel):
    id: str
    title: str
    detail: str
    severity: str
    created_at: datetime


class PlatformInsightsResponse(BaseModel):
    activity_trend: list[TrendPoint]
    industries: list[DistributionItem]
    evaluation_statuses: list[DistributionItem]
    alerts: list[AdminAlertResponse]
