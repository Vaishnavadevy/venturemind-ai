"""Extended administrator CRUD and advisor-verification routes."""

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import Response

from app.api.dependencies import CurrentUser, DatabaseSession, require_role
from app.models.enums import UserRole
from app.models.admin_management import AdvisorVerificationRequest
from app.models.user import User
from app.schemas.admin import AdminUserResponse
from app.schemas.admin_management import (
    AdminCreateUserRequest,
    AdvisorApplicationCreate,
    AdvisorApplicationDetailResponse,
    AdvisorApplicationReview,
    AIUsageResponse,
    AuditLogResponse,
    ContentCreateRequest,
    ContentResponse,
    ContentUpdateRequest,
)
from app.schemas.common import APIResponse
from app.services.admin_management_service import AdvisorVerificationService, AdminMonitoringService, AuditService, ContentManagementService
from app.services.advisor_document_service import AdvisorDocumentService

router = APIRouter()
admin_required = Depends(require_role(UserRole.ADMIN))


@router.get("/content", response_model=APIResponse[list[ContentResponse]])
def published_content(session: DatabaseSession) -> APIResponse[list[ContentResponse]]:
    return APIResponse(data=[ContentResponse.model_validate(item) for item in ContentManagementService(session).list_published()])


@router.post("/advisor-applications", response_model=APIResponse[AdvisorApplicationDetailResponse], status_code=status.HTTP_201_CREATED)
def apply_as_advisor(payload: AdvisorApplicationCreate, user: CurrentUser, session: DatabaseSession) -> APIResponse[AdvisorApplicationDetailResponse]:
    service = AdvisorVerificationService(session)
    item = service.apply(user, payload)
    return APIResponse(data=service.detail_response(item), message="Your verification request was submitted for review.")


@router.get("/advisor-applications/mine", response_model=APIResponse[list[AdvisorApplicationDetailResponse]])
def my_advisor_applications(user: CurrentUser, session: DatabaseSession) -> APIResponse[list[AdvisorApplicationDetailResponse]]:
    service = AdvisorVerificationService(session)
    return APIResponse(data=[service.detail_response(item) for item in service.list_mine(user)])


@router.post("/advisor-applications/{request_id}/documents", response_model=APIResponse[AdvisorApplicationDetailResponse], status_code=status.HTTP_201_CREATED)
async def upload_advisor_document(request_id: str, user: CurrentUser, session: DatabaseSession, document: UploadFile = File(...)) -> APIResponse[AdvisorApplicationDetailResponse]:
    request = session.get(AdvisorVerificationRequest, request_id)
    if not request or request.applicant_id != user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Advisor verification request was not found.")
    await AdvisorDocumentService(session).upload(request_id, document)
    return APIResponse(data=AdvisorVerificationService(session).detail_response(request), message="Verification document stored securely.")


@router.get("/admin/content", response_model=APIResponse[list[ContentResponse]])
def admin_content(session: DatabaseSession, _: User = admin_required) -> APIResponse[list[ContentResponse]]:
    return APIResponse(data=[ContentResponse.model_validate(item) for item in ContentManagementService(session).list_admin()])


@router.post("/admin/content", response_model=APIResponse[ContentResponse], status_code=status.HTTP_201_CREATED)
def create_content(payload: ContentCreateRequest, session: DatabaseSession, user: User = admin_required) -> APIResponse[ContentResponse]:
    return APIResponse(data=ContentResponse.model_validate(ContentManagementService(session).create(user, payload)))


@router.patch("/admin/content/{content_id}", response_model=APIResponse[ContentResponse])
def update_content(content_id: str, payload: ContentUpdateRequest, session: DatabaseSession, user: User = admin_required) -> APIResponse[ContentResponse]:
    return APIResponse(data=ContentResponse.model_validate(ContentManagementService(session).update(user, content_id, payload)))


@router.delete("/admin/content/{content_id}", response_model=APIResponse[None])
def delete_content(content_id: str, session: DatabaseSession, user: User = admin_required) -> APIResponse[None]:
    ContentManagementService(session).delete(user, content_id)
    return APIResponse(data=None, message="Content item deleted.")


@router.post("/admin/users", response_model=APIResponse[AdminUserResponse], status_code=status.HTTP_201_CREATED)
def create_user(payload: AdminCreateUserRequest, session: DatabaseSession, user: User = admin_required) -> APIResponse[AdminUserResponse]:
    return APIResponse(data=AdminUserResponse.model_validate(AdminMonitoringService(session).create_user(user, payload)))


@router.delete("/admin/users/{user_id}", response_model=APIResponse[None])
def delete_user(user_id: str, session: DatabaseSession, user: User = admin_required) -> APIResponse[None]:
    AdminMonitoringService(session).delete_user(user, user_id)
    return APIResponse(data=None, message="User deleted.")


@router.get("/admin/ai-usage", response_model=APIResponse[AIUsageResponse])
def ai_usage(session: DatabaseSession, _: User = admin_required) -> APIResponse[AIUsageResponse]:
    return APIResponse(data=AdminMonitoringService(session).ai_usage())


@router.get("/admin/audit-logs", response_model=APIResponse[list[AuditLogResponse]])
def audit_logs(session: DatabaseSession, _: User = admin_required) -> APIResponse[list[AuditLogResponse]]:
    return APIResponse(data=AdminMonitoringService(session).audit_logs())


@router.get("/admin/advisor-applications", response_model=APIResponse[list[AdvisorApplicationDetailResponse]])
def advisor_applications(session: DatabaseSession, _: User = admin_required) -> APIResponse[list[AdvisorApplicationDetailResponse]]:
    service = AdvisorVerificationService(session)
    return APIResponse(data=[service.detail_response(item) for item in service.list_admin()])


@router.patch("/admin/advisor-applications/{request_id}", response_model=APIResponse[AdvisorApplicationDetailResponse])
def review_advisor_application(request_id: str, payload: AdvisorApplicationReview, session: DatabaseSession, user: User = admin_required) -> APIResponse[AdvisorApplicationDetailResponse]:
    service = AdvisorVerificationService(session)
    return APIResponse(data=service.detail_response(service.review(user, request_id, payload)))


@router.get("/admin/advisor-applications/{request_id}/documents/{document_id}")
def download_advisor_document(request_id: str, document_id: str, session: DatabaseSession, user: User = admin_required) -> Response:
    document, raw = AdvisorDocumentService(session).read_for_admin(request_id, document_id)
    AuditService.record(session, user, "advisor_document.viewed", "advisor_verification_document", document.id, {"request_id": request_id})
    session.commit()
    safe_name = document.original_name.replace('"', "")
    return Response(content=raw, media_type=document.content_type, headers={"Content-Disposition": f'inline; filename="{safe_name}"', "Cache-Control": "no-store"})
