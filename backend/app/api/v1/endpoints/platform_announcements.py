"""Authenticated announcement delivery and administrator management routes."""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import CurrentUser, DatabaseSession, require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.platform_announcements import (
    PlatformAnnouncementCreate,
    PlatformAnnouncementResponse,
    PlatformAnnouncementUpdate,
)
from app.services.platform_announcement_service import PlatformAnnouncementService

router = APIRouter()
admin_required = Depends(require_role(UserRole.ADMIN))


@router.get("/announcements/mine", response_model=APIResponse[list[PlatformAnnouncementResponse]])
def my_announcements(user: CurrentUser, session: DatabaseSession) -> APIResponse[list[PlatformAnnouncementResponse]]:
    items = PlatformAnnouncementService(session).list_for_user(user)
    return APIResponse(data=[PlatformAnnouncementResponse.model_validate(item) for item in items])


@router.get("/admin/announcements", response_model=APIResponse[list[PlatformAnnouncementResponse]])
def announcements(session: DatabaseSession, _: User = admin_required) -> APIResponse[list[PlatformAnnouncementResponse]]:
    items = PlatformAnnouncementService(session).list_for_admin()
    return APIResponse(data=[PlatformAnnouncementResponse.model_validate(item) for item in items])


@router.post("/admin/announcements", response_model=APIResponse[PlatformAnnouncementResponse], status_code=status.HTTP_201_CREATED)
def create_announcement(payload: PlatformAnnouncementCreate, session: DatabaseSession, user: User = admin_required) -> APIResponse[PlatformAnnouncementResponse]:
    item = PlatformAnnouncementService(session).create(user, payload)
    return APIResponse(data=PlatformAnnouncementResponse.model_validate(item), message="Announcement published.")


@router.patch("/admin/announcements/{announcement_id}", response_model=APIResponse[PlatformAnnouncementResponse])
def update_announcement(announcement_id: str, payload: PlatformAnnouncementUpdate, session: DatabaseSession, _: User = admin_required) -> APIResponse[PlatformAnnouncementResponse]:
    if payload.is_active is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Provide an announcement status change.")
    item = PlatformAnnouncementService(session).set_active(_, announcement_id, payload.is_active)
    return APIResponse(data=PlatformAnnouncementResponse.model_validate(item))
