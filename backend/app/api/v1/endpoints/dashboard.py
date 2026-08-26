"""Authenticated founder dashboard endpoint."""

from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import APIResponse
from app.schemas.dashboard import DashboardSnapshot
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard")


@router.get("", response_model=APIResponse[DashboardSnapshot])
def get_dashboard(user: CurrentUser, session: DatabaseSession) -> APIResponse[DashboardSnapshot]:
    return APIResponse(data=DashboardService(session).snapshot(user))
