"""Authenticated startup lifecycle workspace endpoints."""

from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import APIResponse
from app.schemas.lifecycle import LifecycleMilestoneResponse, LifecycleRiskAssessmentResponse, MilestoneUpdate, ProfileSuggestionRequest, ProfileSuggestionResponse, StartupProfileResponse, StartupProfileUpsert
from app.services.lifecycle_service import LifecycleService
from app.services.profile_suggestion_service import ProfileSuggestionService

router = APIRouter(prefix="/lifecycle-profiles")


@router.post("/suggestions", response_model=APIResponse[ProfileSuggestionResponse])
def suggest_profile_fields(payload: ProfileSuggestionRequest, user: CurrentUser) -> APIResponse[ProfileSuggestionResponse]:
    suggestions, mode, notice = ProfileSuggestionService().suggest(payload)
    return APIResponse(data=ProfileSuggestionResponse(suggestions=suggestions, mode=mode, notice=notice))


@router.get("", response_model=APIResponse[list[StartupProfileResponse]])
def list_profiles(user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=[StartupProfileResponse.model_validate(item) for item in LifecycleService(session).list_profiles(user)])


@router.post("", response_model=APIResponse[StartupProfileResponse], status_code=status.HTTP_201_CREATED)
def create_profile(payload: StartupProfileUpsert, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=StartupProfileResponse.model_validate(LifecycleService(session).create_profile(user, payload)))


@router.patch("/{profile_id}", response_model=APIResponse[StartupProfileResponse])
def update_profile(profile_id: str, payload: StartupProfileUpsert, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=StartupProfileResponse.model_validate(LifecycleService(session).update_profile(user, profile_id, payload)))


@router.get("/{profile_id}/milestones", response_model=APIResponse[list[LifecycleMilestoneResponse]])
def list_milestones(profile_id: str, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=[LifecycleMilestoneResponse.model_validate(item) for item in LifecycleService(session).milestones(user, profile_id)])


@router.put("/{profile_id}/milestones/{milestone_key}", response_model=APIResponse[LifecycleMilestoneResponse])
def update_milestone(profile_id: str, milestone_key: str, payload: MilestoneUpdate, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=LifecycleMilestoneResponse.model_validate(LifecycleService(session).set_milestone(user, profile_id, milestone_key, payload.completed)) )


@router.post("/{profile_id}/risk-assessments", response_model=APIResponse[LifecycleRiskAssessmentResponse], status_code=status.HTTP_201_CREATED)
def create_risk_assessment(profile_id: str, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=LifecycleRiskAssessmentResponse.model_validate(LifecycleService(session).assess_risk(user, profile_id)))


@router.get("/{profile_id}/risk-assessments/latest", response_model=APIResponse[LifecycleRiskAssessmentResponse])
def get_latest_risk_assessment(profile_id: str, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=LifecycleRiskAssessmentResponse.model_validate(LifecycleService(session).latest_risk_assessment(user, profile_id)))
