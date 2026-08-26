"""Lifecycle AI advisor contracts."""

from pydantic import BaseModel, Field


class AdvisorRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    conversation_id: str | None = None


class AdvisorResponse(BaseModel):
    response: str
    mode: str
    conversation_id: str
    notice: str | None = None
