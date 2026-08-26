"""Use cases for administrator announcements."""

from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.enums import UserRole
from app.models.platform_announcement import PlatformAnnouncement
from app.models.user import User
from app.schemas.platform_announcements import PlatformAnnouncementCreate
from app.services.admin_management_service import AuditService


class PlatformAnnouncementService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, admin: User, payload: PlatformAnnouncementCreate) -> PlatformAnnouncement:
        announcement = PlatformAnnouncement(
            title=payload.title.strip(),
            message=payload.message.strip(),
            audience=payload.audience,
            expires_at=payload.expires_at,
            created_by_id=admin.id,
        )
        self.session.add(announcement)
        self.session.flush()
        AuditService.record(self.session, admin, "announcement.created", "platform_announcement", announcement.id, {"audience": announcement.audience})
        self.session.commit()
        self.session.refresh(announcement)
        return announcement

    def list_for_admin(self) -> list[PlatformAnnouncement]:
        return list(self.session.scalars(select(PlatformAnnouncement).order_by(PlatformAnnouncement.created_at.desc()).limit(100)))

    def list_for_user(self, user: User) -> list[PlatformAnnouncement]:
        audiences = ["all"]
        if user.role in {UserRole.USER, UserRole.FOUNDER}:
            audiences.append("founders")
        if user.role in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
            audiences.append("advisors")
        now = datetime.now(UTC)
        statement = (
            select(PlatformAnnouncement)
            .where(
                PlatformAnnouncement.is_active.is_(True),
                PlatformAnnouncement.audience.in_(audiences),
                or_(PlatformAnnouncement.expires_at.is_(None), PlatformAnnouncement.expires_at > now),
            )
            .order_by(PlatformAnnouncement.created_at.desc())
            .limit(10)
        )
        return list(self.session.scalars(statement))

    def set_active(self, actor: User, announcement_id: str, is_active: bool) -> PlatformAnnouncement:
        announcement = self.session.get(PlatformAnnouncement, announcement_id)
        if not announcement:
            raise ResourceNotFoundError("Announcement was not found.")
        announcement.is_active = is_active
        AuditService.record(self.session, actor, "announcement.updated", "platform_announcement", announcement.id, {"is_active": is_active})
        self.session.commit()
        self.session.refresh(announcement)
        return announcement
