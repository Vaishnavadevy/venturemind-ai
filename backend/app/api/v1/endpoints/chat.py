from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import APIResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/projects/{project_id}/chat")


@router.post("", response_model=APIResponse[ChatResponse])
def chat(
    project_id: str, payload: ChatRequest, user: CurrentUser, session: DatabaseSession
) -> APIResponse[ChatResponse]:
    conversation_id, response = ChatService(session).ask(
        project_id, user, payload.message, payload.conversation_id
    )
    return APIResponse(data=ChatResponse(conversation_id=conversation_id, response=response))
