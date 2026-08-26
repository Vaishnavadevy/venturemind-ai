from fastapi import APIRouter
from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.advisor import AdvisorRequest, AdvisorResponse
from app.schemas.common import APIResponse
from app.services.lifecycle_advisor_service import LifecycleAdvisorService

router = APIRouter(prefix="/lifecycle-profiles/{profile_id}/advisor")

@router.post("", response_model=APIResponse[AdvisorResponse])
def ask_advisor(profile_id: str, payload: AdvisorRequest, user: CurrentUser, session: DatabaseSession):
    conversation_id, response, mode, notice = LifecycleAdvisorService(session).ask(user, profile_id, payload.question, payload.conversation_id)
    return APIResponse(data=AdvisorResponse(response=response, mode=mode, conversation_id=conversation_id, notice=notice))


@router.post("/quick", response_model=APIResponse[AdvisorResponse])
def ask_advisor_without_chat_history(profile_id: str, payload: AdvisorRequest, user: CurrentUser, session: DatabaseSession):
    """Use local Ollama with saved startup context when chat persistence is unavailable."""
    conversation_id, response, mode, notice = LifecycleAdvisorService(session).ask_without_persistence(user, profile_id, payload.question)
    return APIResponse(data=AdvisorResponse(response=response, mode=mode, conversation_id=conversation_id, notice=notice))
