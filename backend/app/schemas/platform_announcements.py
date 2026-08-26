"""Request and response contracts for platform announcements."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AnnouncementAudience = Literal["all", "founders", "advisors"]


class PlatformAnnouncementCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    message: str = Field(min_length=3, max_length=5000)
    audience: AnnouncementAudience = "all"
    expires_at: datetime | None = None


class PlatformAnnouncementUpdate(BaseModel):
    is_active: bool | None = None


class PlatformAnnouncementResponse(PlatformAnnouncementCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_at: datetime
