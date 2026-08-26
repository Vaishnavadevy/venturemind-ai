"""Founder dashboard recommendations derived from existing saved business data."""

from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import APIResponse
from app.schemas.smart_recommendations import SmartRecommendationResponse, SmartRecommendationSnapshot, SmartRecommendationStatusUpdate
from app.services.smart_recommendation_service import SmartRecommendationService

router = APIRouter(prefix="/recommendations")


@router.get("/current", response_model=APIResponse[SmartRecommendationSnapshot])
def current_recommendations(user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=SmartRecommendationService(session).current(user))


@router.patch("/{recommendation_key}", response_model=APIResponse[SmartRecommendationResponse])
def update_recommendation(recommendation_key: str, payload: SmartRecommendationStatusUpdate, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=SmartRecommendationService(session).set_completed(user, recommendation_key, payload.completed))
