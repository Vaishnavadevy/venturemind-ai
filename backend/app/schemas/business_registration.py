"""Read/write contracts for the educational registration guide."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


RegistrationStatus = Literal["not_started", "in_progress", "completed", "waiting_for_review", "approved", "requires_action"]


class RegistrationJourneyStart(BaseModel):
    mode: Literal["guide", "demo"] = "guide"


class RegistrationJourneyUpdate(BaseModel):
    company_type: str | None = Field(default=None, max_length=120)
    proposed_company_name: str | None = Field(default=None, max_length=180)


class RegistrationItemUpdate(BaseModel):
    status: RegistrationStatus


class RegistrationChecklistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    item_key: str
    step_number: int
    title: str
    description: str
    category: str
    official_url: str | None
    status: RegistrationStatus
    completed_at: datetime | None


class RegistrationResource(BaseModel):
    title: str
    description: str
    url: str
    category: str
    official: bool = True


class RegistrationJourneyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    startup_profile_id: str
    mode: str
    company_type: str | None
    proposed_company_name: str | None
    overall_status: str
    is_demo: bool
    progress_percentage: int
    items: list[RegistrationChecklistItemResponse]
    resources: list[RegistrationResource]
