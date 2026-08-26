"""Authenticated investment-planning endpoints."""

from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import APIResponse
from app.schemas.financial_plan import FinancialPlanInput, FinancialPlanResponse
from app.services.financial_plan_service import FinancialPlanService

router = APIRouter(prefix="/lifecycle-profiles/{profile_id}/financial-plans")


@router.post("", response_model=APIResponse[FinancialPlanResponse], status_code=status.HTTP_201_CREATED)
def create_financial_plan(profile_id: str, payload: FinancialPlanInput, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=FinancialPlanResponse.model_validate(FinancialPlanService(session).create(user, profile_id, payload)))


@router.get("/latest", response_model=APIResponse[FinancialPlanResponse])
def get_latest_financial_plan(profile_id: str, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=FinancialPlanResponse.model_validate(FinancialPlanService(session).latest(user, profile_id)))
