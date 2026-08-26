"""Administrator-only API endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import DatabaseSession, require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.admin import (
    AdminUserResponse,
    AnalyticsResponse,
    PlatformInsightsResponse,
    FeedbackResponse,
    UpdateFeedbackRequest,
    UpdateUserStatusRequest,
)
from app.schemas.common import APIResponse
from app.services.admin_service import AdminService
from app.services.admin_management_service import AuditService

router = APIRouter(prefix="/admin")
admin_required = Depends(require_role(UserRole.ADMIN))


@router.get("/analytics", response_model=APIResponse[AnalyticsResponse])
def analytics(session: DatabaseSession, _: User = admin_required) -> APIResponse[AnalyticsResponse]:
    return APIResponse(data=AdminService(session).analytics())


@router.get("/platform-insights", response_model=APIResponse[PlatformInsightsResponse])
def platform_insights(
    session: DatabaseSession, _: User = admin_required
) -> APIResponse[PlatformInsightsResponse]:
    return APIResponse(data=AdminService(session).platform_insights())


@router.get("/users", response_model=APIResponse[list[AdminUserResponse]])
def users(
    session: DatabaseSession, _: User = admin_required
) -> APIResponse[list[AdminUserResponse]]:
    return APIResponse(
        data=[AdminUserResponse.model_validate(user) for user in AdminService(session).users()]
    )


@router.patch("/users/{user_id}", response_model=APIResponse[AdminUserResponse])
def update_user(
    user_id: str,
    payload: UpdateUserStatusRequest,
    session: DatabaseSession,
    current_user: User = admin_required,
) -> APIResponse[AdminUserResponse]:
    if payload.role in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Advisor roles are assigned only after the advisor verification review.")
    if user_id == current_user.id:
        # Prevent an administrator from accidentally removing their own access.
        if payload.is_active is False or (payload.role is not None and payload.role != UserRole.ADMIN):
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove your own administrator access.")
    updated = AdminService(session).update_user(
        user_id,
        is_active=payload.is_active,
        role=payload.role,
        is_email_verified=payload.is_email_verified,
    )
    AuditService.record(session, current_user, "user.updated", "user", updated.id, payload.model_dump(exclude_none=True))
    session.commit()
    return APIResponse(data=AdminUserResponse.model_validate(updated))


@router.get("/feedback", response_model=APIResponse[list[FeedbackResponse]])
def feedback(
    session: DatabaseSession, _: User = admin_required
) -> APIResponse[list[FeedbackResponse]]:
    return APIResponse(
        data=[FeedbackResponse.model_validate(item) for item in AdminService(session).feedback()]
    )


@router.patch("/feedback/{feedback_id}", response_model=APIResponse[FeedbackResponse])
def update_feedback(
    feedback_id: str,
    payload: UpdateFeedbackRequest,
    session: DatabaseSession,
    _: User = admin_required,
) -> APIResponse[FeedbackResponse]:
    service = AdminService(session)
    updated = service.update_feedback(feedback_id, payload.status, payload.admin_note)
    AuditService.record(session, _, "feedback.updated", "feedback", updated.id, {"status": payload.status.value})
    session.commit()
    return APIResponse(data=FeedbackResponse.model_validate(updated))
