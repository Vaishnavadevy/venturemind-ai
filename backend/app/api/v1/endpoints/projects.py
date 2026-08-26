"""Authenticated project-submission endpoints."""

from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import APIResponse
from app.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    ProjectSubmissionResponse,
    StartupIdeaResponse,
)
from app.services.evaluation_service import EvaluationService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects")


@router.post(
    "", response_model=APIResponse[ProjectSubmissionResponse], status_code=status.HTTP_201_CREATED
)
def create_project(
    payload: CreateProjectRequest,
    user: CurrentUser,
    session: DatabaseSession,
) -> APIResponse[ProjectSubmissionResponse]:
    project, idea = ProjectService(session).create_project(user, payload)
    evaluation = EvaluationService(session).evaluate_idea(project, idea)
    return APIResponse(
        data=ProjectSubmissionResponse(
            project=ProjectResponse.model_validate(project),
            startup_idea=StartupIdeaResponse.model_validate(idea),
            evaluation_id=evaluation.id,
        ),
        message="Startup idea submitted and evaluated.",
    )
