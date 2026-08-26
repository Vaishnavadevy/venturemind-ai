"""Public contact-form endpoint for feedback that administrators can review."""

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

from app.api.dependencies import DatabaseSession
from app.models.enums import FeedbackStatus
from app.models.feedback import Feedback
from app.schemas.common import APIResponse

router = APIRouter(prefix="/public-feedback")


class PublicFeedbackRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    message: str = Field(min_length=10, max_length=4000)
    category: str = Field(default="Contact message", min_length=2, max_length=64)


class PublicFeedbackResponse(BaseModel):
    id: str
    status: FeedbackStatus
    message: str


@router.post("", response_model=APIResponse[PublicFeedbackResponse], status_code=201)
def submit_public_feedback(payload: PublicFeedbackRequest, session: DatabaseSession) -> APIResponse[PublicFeedbackResponse]:
    """Persist a public contact message for the administrator feedback queue."""
    feedback = Feedback(user_id=None, contact_name=payload.name.strip(), contact_email=str(payload.email).lower(), category=payload.category.strip(), message=payload.message.strip(), status=FeedbackStatus.OPEN)
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return APIResponse(data=PublicFeedbackResponse(id=feedback.id, status=feedback.status, message="Your message was sent to the VentureMind administration team."))
