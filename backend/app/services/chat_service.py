from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_client import GeminiClient
from app.core.exceptions import ResourceNotFoundError
from app.models.chat import ChatConversation, ChatMessage
from app.models.evaluation import Evaluation
from app.models.project import Project
from app.models.user import User


class ChatService:
    def __init__(self, session: Session):
        self.session = session

    def ask(
        self, project_id: str, user: User, message: str, conversation_id: str | None
    ) -> tuple[str, str]:
        project = self.session.scalar(
            select(Project).where(Project.id == project_id, Project.owner_id == user.id)
        )
        if not project:
            raise ResourceNotFoundError("Project was not found.")
        conversation = (
            self.session.get(ChatConversation, conversation_id) if conversation_id else None
        )
        if conversation and (
            conversation.user_id != user.id or conversation.project_id != project_id
        ):
            raise ResourceNotFoundError("Conversation was not found.")
        if not conversation:
            conversation = ChatConversation(
                user_id=user.id, project_id=project_id, title=message[:80]
            )
            self.session.add(conversation)
            self.session.flush()
        history = self.session.scalars(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.sequence_number)
        ).all()
        evaluation = self.session.scalar(
            select(Evaluation)
            .where(Evaluation.project_id == project_id)
            .order_by(Evaluation.created_at.desc())
        )
        sequence = len(history) + 1
        self.session.add(
            ChatMessage(
                conversation_id=conversation.id,
                sequence_number=sequence,
                role="user",
                content=message,
            )
        )
        context = f"Project: {project.name}. Latest confidence score: {evaluation.overall_confidence_score if evaluation else 'not evaluated'}. Recommendations: {evaluation.recommendations if evaluation else 'evaluate first'}."
        transcript = "\n".join(f"{item.role}: {item.content}" for item in history[-8:])
        answer = GeminiClient().generate(
            f"You are VentureMind AI, a concise startup advisor. Use only this context and say when evidence is missing.\n{context}\n{transcript}\nUser: {message}"
        )
        self.session.add(
            ChatMessage(
                conversation_id=conversation.id,
                sequence_number=sequence + 1,
                role="assistant",
                content=answer,
                model="gemini",
            )
        )
        self.session.commit()
        return conversation.id, answer
