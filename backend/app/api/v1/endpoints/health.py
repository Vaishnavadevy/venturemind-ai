"""Operational health endpoints."""

from fastapi import APIRouter, status

from app.core.config import get_settings
from app.schemas.common import APIResponse, HealthStatus

router = APIRouter(prefix="/health")


@router.get("", response_model=APIResponse[HealthStatus], status_code=status.HTTP_200_OK)
def get_health() -> APIResponse[HealthStatus]:
    """Return a lightweight liveness response without touching external services."""
    settings = get_settings()
    return APIResponse(data=HealthStatus(environment=settings.app_env))
