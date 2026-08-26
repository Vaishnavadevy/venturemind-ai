"""Database-backed administration use cases."""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ResourceNotFoundError
from app.core.security import hash_password
from app.models.admin_management import AdvisorProfile, AdvisorVerificationDocument, AdvisorVerificationRequest, AuditLog, ContentItem
from app.models.enums import EvaluationStatus, UserRole
from app.models.evaluation import Evaluation
from app.models.project import Project
from app.models.user import User
from app.schemas.admin_management import (
    AdminCreateUserRequest,
    AdvisorApplicationCreate,
    AdvisorApplicationDetailResponse,
    AdvisorApplicationResponse,
    AdvisorApplicationReview,
    AIUsageEvaluationResponse,
    AIUsageResponse,
    AuditLogResponse,
    ContentCreateRequest,
    ContentUpdateRequest,
)


class AuditService:
    @staticmethod
    def record(session: Session, actor: User | None, action: str, target_type: str, target_id: str | None, detail: dict[str, object] | None = None) -> None:
        session.add(AuditLog(actor_id=actor.id if actor else None, action=action, target_type=target_type, target_id=target_id, detail=detail))


class ContentManagementService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_admin(self) -> list[ContentItem]:
        return list(self.session.scalars(select(ContentItem).order_by(ContentItem.created_at.desc()).limit(200)))

    def list_published(self) -> list[ContentItem]:
        return list(self.session.scalars(select(ContentItem).where(ContentItem.is_published.is_(True)).order_by(ContentItem.created_at.desc()).limit(50)))

    def create(self, actor: User, payload: ContentCreateRequest) -> ContentItem:
        item = ContentItem(**payload.model_dump(), created_by_id=actor.id)
        self.session.add(item)
        self.session.flush()
        AuditService.record(self.session, actor, "content.created", "content_item", item.id, {"content_type": item.content_type, "published": item.is_published})
        self.session.commit(); self.session.refresh(item)
        return item

    def update(self, actor: User, item_id: str, payload: ContentUpdateRequest) -> ContentItem:
        item = self.session.get(ContentItem, item_id)
        if not item: raise ResourceNotFoundError("Content item was not found.")
        changes = payload.model_dump(exclude_unset=True)
        for key, value in changes.items(): setattr(item, key, value)
        AuditService.record(self.session, actor, "content.updated", "content_item", item.id, {"fields": list(changes)})
        self.session.commit(); self.session.refresh(item)
        return item

    def delete(self, actor: User, item_id: str) -> None:
        item = self.session.get(ContentItem, item_id)
        if not item: raise ResourceNotFoundError("Content item was not found.")
        AuditService.record(self.session, actor, "content.deleted", "content_item", item.id, {"title": item.title})
        self.session.delete(item); self.session.commit()


class AdvisorVerificationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def apply(self, user: User, payload: AdvisorApplicationCreate) -> AdvisorVerificationRequest:
        existing = self.session.scalar(select(AdvisorVerificationRequest).where(AdvisorVerificationRequest.applicant_id == user.id, AdvisorVerificationRequest.status == "pending"))
        if existing: raise ConflictError("You already have a verification request awaiting review.")
        if not payload.privacy_consent or not payload.retention_accepted:
            raise ConflictError("Privacy consent and the verification-data retention policy must be accepted.")
        request = AdvisorVerificationRequest(
            applicant_id=user.id,
            retention_until=date.today() + timedelta(days=365),
            **payload.model_dump(),
        )
        self.session.add(request)
        self.session.flush()
        AuditService.record(self.session, user, "advisor_application.submitted", "advisor_verification_request", request.id, {"requested_role": request.requested_role})
        self.session.commit(); self.session.refresh(request)
        return request

    def list_admin(self) -> list[AdvisorVerificationRequest]:
        return list(self.session.scalars(select(AdvisorVerificationRequest).order_by(AdvisorVerificationRequest.created_at.desc()).limit(200)))

    def list_mine(self, user: User) -> list[AdvisorVerificationRequest]:
        return list(self.session.scalars(select(AdvisorVerificationRequest).where(AdvisorVerificationRequest.applicant_id == user.id).order_by(AdvisorVerificationRequest.created_at.desc())))

    def review(self, actor: User, request_id: str, payload: AdvisorApplicationReview) -> AdvisorVerificationRequest:
        request = self.session.get(AdvisorVerificationRequest, request_id)
        if not request: raise ResourceNotFoundError("Advisor verification request was not found.")
        if request.status != "pending": raise ConflictError("This verification request has already been reviewed.")
        documents = self.session.scalar(select(func.count()).select_from(AdvisorVerificationDocument).where(AdvisorVerificationDocument.verification_request_id == request.id)) or 0
        if payload.status == "approved" and not documents:
            raise ConflictError("At least one encrypted verification document is required before approval.")
        if payload.status == "approved" and (not payload.licence_valid or not payload.professional_body_verified):
            raise ConflictError("Confirm licence validity and professional-body verification before approval.")
        request.status = payload.status; request.reviewer_note = payload.reviewer_note; request.reviewed_by_id = actor.id; request.reviewed_at = datetime.now(UTC)
        applicant = self.session.get(User, request.applicant_id)
        if payload.status == "approved" and applicant:
            applicant.role = UserRole(request.requested_role); applicant.is_active = True; applicant.is_email_verified = True
            profile = self.session.scalar(select(AdvisorProfile).where(AdvisorProfile.user_id == applicant.id))
            profile_values = {
                "photo_url": request.photo_url,
                "bio": request.bio or request.professional_summary,
                "specialisation": request.specialisation or "Professional advisory services",
                "languages": request.languages,
                "consultation_fee": request.consultation_fee,
                "availability": request.availability,
                "professional_body": request.professional_body,
                "credential_expiry": payload.credential_expiry,
                "is_visible": True,
            }
            if profile:
                for field, value in profile_values.items(): setattr(profile, field, value)
            else:
                self.session.add(AdvisorProfile(user_id=applicant.id, **profile_values))
        request.licence_valid = payload.licence_valid
        request.professional_body_verified = payload.professional_body_verified
        request.credential_expiry = payload.credential_expiry
        AuditService.record(self.session, actor, f"advisor_application.{payload.status}", "advisor_verification_request", request.id, {"applicant_id": request.applicant_id, "requested_role": request.requested_role})
        self.session.commit(); self.session.refresh(request)
        return request

    def response(self, request: AdvisorVerificationRequest) -> AdvisorApplicationResponse:
        applicant = self.session.get(User, request.applicant_id)
        return AdvisorApplicationResponse.model_validate({**{field: getattr(request, field) for field in AdvisorApplicationResponse.model_fields if hasattr(request, field)}, "applicant_name": applicant.full_name if applicant else None, "applicant_email": applicant.email if applicant else None})

    def detail_response(self, request: AdvisorVerificationRequest) -> AdvisorApplicationDetailResponse:
        base = self.response(request).model_dump()
        documents = self.session.scalars(select(AdvisorVerificationDocument).where(AdvisorVerificationDocument.verification_request_id == request.id).order_by(AdvisorVerificationDocument.created_at.desc())).all()
        return AdvisorApplicationDetailResponse.model_validate({**base, "documents": documents})


class AdminMonitoringService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_user(self, actor: User, payload: AdminCreateUserRequest) -> User:
        if self.session.scalar(select(User).where(User.email == str(payload.email).lower())): raise ConflictError("An account with this email address already exists.")
        user = User(full_name=payload.full_name.strip(), email=str(payload.email).lower(), password_hash=hash_password(payload.password), role=UserRole(payload.role), is_active=True, is_email_verified=payload.is_email_verified)
        self.session.add(user); self.session.flush()
        if user.role in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
            self.session.add(AdvisorProfile(user_id=user.id, specialisation=payload.specialisation or ("Business registration, licences, and compliance" if user.role == UserRole.LEGAL_ADVISOR else "Startup validation, growth, and operations"), professional_body=payload.professional_body, consultation_fee=payload.consultation_fee, languages=payload.languages, bio=payload.bio, availability=[], is_visible=True))
        AuditService.record(self.session, actor, "user.created", "user", user.id, {"role": payload.role})
        self.session.commit(); self.session.refresh(user)
        return user

    def delete_user(self, actor: User, user_id: str) -> None:
        if actor.id == user_id: raise ConflictError("You cannot delete your own administrator account.")
        user = self.session.get(User, user_id)
        if not user: raise ResourceNotFoundError("User was not found.")
        user.is_active = False; user.is_archived = True; user.archived_at = datetime.now(UTC)
        AuditService.record(self.session, actor, "user.archived", "user", user.id, {"email": user.email, "role": user.role.value})
        self.session.commit()

    def ai_usage(self) -> AIUsageResponse:
        evaluations = list(self.session.scalars(select(Evaluation).order_by(Evaluation.created_at.desc()).limit(25)))
        total = self.session.scalar(select(func.count()).select_from(Evaluation)) or 0
        complete = self.session.scalar(select(func.count()).select_from(Evaluation).where(Evaluation.status == EvaluationStatus.COMPLETED)) or 0
        failed = self.session.scalar(select(func.count()).select_from(Evaluation).where(Evaluation.status == EvaluationStatus.FAILED)) or 0
        input_tokens = self.session.scalar(select(func.coalesce(func.sum(Evaluation.input_tokens), 0))) or 0
        output_tokens = self.session.scalar(select(func.coalesce(func.sum(Evaluation.output_tokens), 0))) or 0
        rows: list[AIUsageEvaluationResponse] = []
        for evaluation in evaluations:
            project = self.session.get(Project, evaluation.project_id)
            rows.append(AIUsageEvaluationResponse(id=evaluation.id, project_name=project.name if project else "Deleted project", status=evaluation.status.value, input_tokens=evaluation.input_tokens or 0, output_tokens=evaluation.output_tokens or 0, created_at=evaluation.created_at))
        return AIUsageResponse(total_requests=total, completed_requests=complete, failed_requests=failed, input_tokens=input_tokens, output_tokens=output_tokens, recent_evaluations=rows)

    def audit_logs(self) -> list[AuditLogResponse]:
        rows = list(self.session.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)))
        return [AuditLogResponse.model_validate({"id": row.id, "action": row.action, "target_type": row.target_type, "target_id": row.target_id, "detail": row.detail, "actor_name": self.session.get(User, row.actor_id).full_name if row.actor_id and self.session.get(User, row.actor_id) else None, "created_at": row.created_at}) for row in rows]
