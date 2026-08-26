"""Schemas for the extended administration workflow."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

ContentType = Literal["checklist", "template", "success_story", "failure_story", "book", "resource"]
AdvisorDocumentType = Literal["nic", "passport", "professional_registration"]
AdvisorRequestedRole = Literal["legal_advisor", "business_mentor"]


class ContentCreateRequest(BaseModel):
    content_type: ContentType
    title: str = Field(min_length=3, max_length=220)
    summary: str = Field(min_length=10, max_length=10000)
    source_url: str | None = Field(default=None, max_length=600)
    image_url: str | None = Field(default=None, max_length=600)
    is_published: bool = False


class ContentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=220)
    summary: str | None = Field(default=None, min_length=10, max_length=10000)
    source_url: str | None = Field(default=None, max_length=600)
    image_url: str | None = Field(default=None, max_length=600)
    is_published: bool | None = None


class ContentResponse(ContentCreateRequest):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class AdminCreateUserRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    role: Literal["user", "founder", "job_applicant", "investor", "admin"] = "user"
    is_email_verified: bool = True
    specialisation: str | None = Field(default=None, max_length=500)
    professional_body: str | None = Field(default=None, max_length=220)
    consultation_fee: float | None = Field(default=None, ge=0, le=10_000_000)
    languages: list[str] = Field(default_factory=list, max_length=12)
    bio: str | None = Field(default=None, max_length=5000)


class AdvisorApplicationCreate(BaseModel):
    requested_role: AdvisorRequestedRole = "legal_advisor"
    document_type: AdvisorDocumentType
    document_reference: str = Field(min_length=4, max_length=120)
    registration_number: str | None = Field(default=None, max_length=120)
    professional_summary: str = Field(min_length=20, max_length=5000)
    photo_url: str | None = Field(default=None, max_length=600)
    bio: str | None = Field(default=None, max_length=5000)
    specialisation: str = Field(min_length=3, max_length=500)
    languages: list[str] = Field(default_factory=list, max_length=12)
    consultation_fee: float | None = Field(default=None, ge=0, le=10_000_000)
    availability: list[str] = Field(default_factory=list, max_length=28)
    professional_body: str | None = Field(default=None, max_length=220)
    privacy_consent: bool
    retention_accepted: bool


class AdvisorApplicationReview(BaseModel):
    status: Literal["approved", "rejected"]
    reviewer_note: str | None = Field(default=None, max_length=5000)
    licence_valid: bool
    professional_body_verified: bool
    credential_expiry: date | None = None


class AdvisorApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    applicant_id: str
    applicant_name: str | None = None
    applicant_email: str | None = None
    requested_role: str
    document_type: str
    document_reference: str
    registration_number: str | None
    professional_summary: str
    photo_url: str | None
    bio: str | None
    specialisation: str | None
    languages: list[str] | None
    consultation_fee: float | None
    availability: list[str] | None
    professional_body: str | None
    privacy_consent: bool
    retention_accepted: bool
    retention_until: date | None
    status: str
    reviewer_note: str | None
    reviewed_at: datetime | None
    licence_valid: bool | None
    professional_body_verified: bool | None
    credential_expiry: date | None
    created_at: datetime


class AdvisorDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_name: str
    content_type: str
    size_bytes: int
    retention_until: date
    created_at: datetime


class AdvisorApplicationDetailResponse(AdvisorApplicationResponse):
    documents: list[AdvisorDocumentResponse] = Field(default_factory=list)


class AIUsageEvaluationResponse(BaseModel):
    id: str
    project_name: str
    status: str
    input_tokens: int
    output_tokens: int
    created_at: datetime


class AIUsageResponse(BaseModel):
    total_requests: int
    completed_requests: int
    failed_requests: int
    input_tokens: int
    output_tokens: int
    recent_evaluations: list[AIUsageEvaluationResponse]


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    target_type: str
    target_id: str | None
    detail: dict[str, object] | None
    actor_name: str | None = None
    created_at: datetime
