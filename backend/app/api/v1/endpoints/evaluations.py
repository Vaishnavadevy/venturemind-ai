"""Evaluation pipeline endpoints."""

from fastapi import APIRouter, status
from sqlalchemy.orm import selectinload

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.exceptions import ResourceNotFoundError
from app.models.evaluation import Evaluation
from app.schemas.common import APIResponse
from app.schemas.evaluation import EvaluationResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/projects/{project_id}/evaluations")


@router.post(
    "", response_model=APIResponse[EvaluationResponse], status_code=status.HTTP_201_CREATED
)
def create_evaluation(
    project_id: str, user: CurrentUser, session: DatabaseSession
) -> APIResponse[EvaluationResponse]:
    evaluation = EvaluationService(session).evaluate_latest_idea(project_id, user)
    return APIResponse(
        data=EvaluationResponse.model_validate(evaluation), message="Evaluation completed."
    )


@router.get("/{evaluation_id}", response_model=APIResponse[EvaluationResponse])
def get_evaluation(
    project_id: str, evaluation_id: str, user: CurrentUser, session: DatabaseSession
) -> APIResponse[EvaluationResponse]:
    evaluation = session.get(Evaluation, evaluation_id, options=[selectinload(Evaluation.scores)])
    if (
        not evaluation
        or evaluation.project_id != project_id
        or evaluation.project.owner_id != user.id
    ):
        raise ResourceNotFoundError("Evaluation was not found.")
    return APIResponse(data=EvaluationResponse.model_validate(evaluation))
