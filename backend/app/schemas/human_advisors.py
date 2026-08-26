"""Human advisor directory and consultation request contracts."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class HumanAdvisorResponse(BaseModel):
    id: str
    full_name: str
    role: str
    specialisation: str
    consultation_modes: list[str]
    verification_status: str
    photo_url: str | None = None
    bio: str | None = None
    languages: list[str] = Field(default_factory=list)
    consultation_fee: float | None = None
    availability: list[str] = Field(default_factory=list)
    professional_body: str | None = None
    qualifications: str | None = None
    registration_details: str | None = None
    membership_plan: str = "general"
    office_address: str | None = None
    service_fees: list[dict[str, object]] = Field(default_factory=list)


class AdvisorProfileUpdate(BaseModel):
    photo_url: str | None = Field(default=None, max_length=600)
    bio: str | None = Field(default=None, max_length=4000)
    specialisation: str = Field(min_length=3, max_length=500)
    languages: list[str] = Field(default_factory=list)
    consultation_fee: float | None = Field(default=None, ge=0, le=10_000_000)
    professional_body: str | None = Field(default=None, max_length=220)
    qualifications: str | None = Field(default=None, max_length=5000)
    registration_details: str | None = Field(default=None, max_length=500)
    membership_plan: str = Field(default="general", pattern="^(general|silver|platinum)$")
    office_address: str | None = Field(default=None, max_length=500)
    service_fees: list[dict[str, object]] = Field(default_factory=list, max_length=8)


class BookingRequestCreate(BaseModel):
    advisor_id: str
    consultation_type: str = Field(pattern="^(online|in_person)$")
    topic: str = Field(min_length=3, max_length=160)
    message: str = Field(min_length=10, max_length=2000)
    availability_slot_id: str | None = None
    service_name: str | None = Field(default=None, max_length=160)


class BookingRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    advisor_id: str
    consultation_type: str
    topic: str
    message: str
    status: str
    advisor_note: str | None = None
    scheduled_at: datetime | None = None
    created_at: datetime
    meeting_url: str | None = None
    availability_slot_id: str | None = None
    service_name: str = "General consultation"
    quoted_fee_lkr: float = 0


class IncomingBookingResponse(BookingRequestResponse):
    founder_name: str
    founder_email: str


class FounderBookingResponse(BookingRequestResponse):
    advisor_name: str
    advisor_role: str


class BookingRequestUpdate(BaseModel):
    status: str = Field(pattern="^(pending|accepted|declined|cancelled|completed)$")
    advisor_note: str | None = Field(default=None, max_length=2000)
    scheduled_at: datetime | None = None
    meeting_url: str | None = Field(default=None, max_length=600)


class AvailabilitySlotCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime
    consultation_type: str = Field(pattern="^(online|in_person)$")


class AvailabilitySlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    advisor_id: str
    starts_at: datetime
    ends_at: datetime
    consultation_type: str
    is_booked: bool


class BookingPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    booking_request_id: str
    amount_lkr: float
    status: str
    provider: str
    reference: str | None


class BookingMessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class BookingMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    booking_request_id: str
    sender_id: str
    sender_name: str
    body: str
    created_at: datetime


class DocumentRequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    instructions: str | None = Field(default=None, max_length=2000)


class SharedDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    original_name: str
    content_type: str
    size_bytes: int
    reviewed: bool
    created_at: datetime


class DocumentRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    booking_request_id: str
    title: str
    instructions: str | None = None
    status: str
    documents: list[SharedDocumentResponse] = Field(default_factory=list)
    created_at: datetime


class AdvisorWorkspaceSummary(BaseModel):
    profile_visible: bool
    verification_status: str
    completed_consultations: int
    pending_requests: int
    upcoming_appointments: int
    unread_notifications: int
    paid_consultations: int
    monthly_demo_income_lkr: float
    lifetime_demo_income_lkr: float
