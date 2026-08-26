"""Authenticated competitor-discovery endpoints."""

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.schemas.common import APIResponse
from app.schemas.competitor import CompetitorSearchRequest, CompetitorSearchResponse
from app.services.competitor_service import CompetitorService

router = APIRouter(prefix="/competitors")


@router.post("/search", response_model=APIResponse[CompetitorSearchResponse])
def search_competitors(payload: CompetitorSearchRequest, _: CurrentUser) -> APIResponse[CompetitorSearchResponse]:
    """Return real Google Places business listings for a founder's location query."""
    return APIResponse(data=CompetitorService().search(payload))
