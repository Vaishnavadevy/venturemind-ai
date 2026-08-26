"""Founder-facing directory for platform advisor accounts."""

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.exceptions import ResourceNotFoundError
from app.models.advisor import AdvisorAvailabilitySlot, AdvisorBookingRequest, AdvisorBookingMessage, AdvisorDocumentRequest, AdvisorSharedDocument
from app.models.admin_management import AdvisorProfile
from app.models.enums import NotificationType, UserRole
from app.models.notification import Notification
from app.models.advisor_payment import AdvisorBookingPayment
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.human_advisors import AdvisorProfileUpdate, AdvisorWorkspaceSummary, AvailabilitySlotCreate, AvailabilitySlotResponse, BookingMessageCreate, BookingMessageResponse, BookingPaymentResponse, BookingRequestCreate, BookingRequestResponse, BookingRequestUpdate, DocumentRequestCreate, DocumentRequestResponse, FounderBookingResponse, HumanAdvisorResponse, IncomingBookingResponse, SharedDocumentResponse
from app.services.booking_document_service import BookingDocumentService

router = APIRouter(prefix="/human-advisors")


@router.get("/workspace-summary", response_model=APIResponse[AdvisorWorkspaceSummary])
def workspace_summary(user: CurrentUser, session: DatabaseSession) -> APIResponse[AdvisorWorkspaceSummary]:
    """Advisor-only operational metrics; payment values are demonstration records."""
    if user.role not in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
        raise ResourceNotFoundError("Advisor workspace is not available for this account.")
    profile = advisor_profile_or_none(session, user.id)
    completed = session.scalar(select(func.count()).select_from(AdvisorBookingRequest).where(AdvisorBookingRequest.advisor_id == user.id, AdvisorBookingRequest.status == "completed")) or 0
    pending = session.scalar(select(func.count()).select_from(AdvisorBookingRequest).where(AdvisorBookingRequest.advisor_id == user.id, AdvisorBookingRequest.status == "pending")) or 0
    upcoming = session.scalar(select(func.count()).select_from(AdvisorBookingRequest).where(AdvisorBookingRequest.advisor_id == user.id, AdvisorBookingRequest.status == "accepted", AdvisorBookingRequest.scheduled_at > datetime.now())) or 0
    unread = session.scalar(select(func.count()).select_from(Notification).where(Notification.user_id == user.id, Notification.is_read.is_(False))) or 0
    payment_rows = session.execute(select(AdvisorBookingPayment.amount_lkr).join(AdvisorBookingRequest, AdvisorBookingPayment.booking_request_id == AdvisorBookingRequest.id).where(AdvisorBookingRequest.advisor_id == user.id, AdvisorBookingPayment.status == "paid")).scalars().all()
    current_month = datetime.now().month
    current_year = datetime.now().year
    month_rows = session.execute(select(AdvisorBookingPayment.amount_lkr).join(AdvisorBookingRequest, AdvisorBookingPayment.booking_request_id == AdvisorBookingRequest.id).where(AdvisorBookingRequest.advisor_id == user.id, AdvisorBookingPayment.status == "paid", func.month(AdvisorBookingPayment.created_at) == current_month, func.year(AdvisorBookingPayment.created_at) == current_year)).scalars().all()
    return APIResponse(data=AdvisorWorkspaceSummary(profile_visible=bool(profile and profile.is_visible), verification_status="Verified platform advisor" if profile else "Profile awaiting approval", completed_consultations=int(completed), pending_requests=int(pending), upcoming_appointments=int(upcoming), unread_notifications=int(unread), paid_consultations=len(payment_rows), monthly_demo_income_lkr=float(sum(month_rows)), lifetime_demo_income_lkr=float(sum(payment_rows))))


@router.post("/booking-requests/{request_id}/payment", response_model=APIResponse[BookingPaymentResponse])
def record_demo_payment(request_id: str, user: CurrentUser, session: DatabaseSession) -> APIResponse[BookingPaymentResponse]:
    booking = session.get(AdvisorBookingRequest, request_id)
    if not booking or booking.founder_id != user.id: raise ResourceNotFoundError("Booking was not found.")
    payment = session.scalar(select(AdvisorBookingPayment).where(AdvisorBookingPayment.booking_request_id == booking.id))
    profile = session.scalar(select(AdvisorProfile).where(AdvisorProfile.user_id == booking.advisor_id))
    amount = float(booking.quoted_fee_lkr) if booking.quoted_fee_lkr is not None else (float(profile.consultation_fee) if profile and profile.consultation_fee is not None else 0.0)
    if not payment:
        payment = AdvisorBookingPayment(booking_request_id=booking.id, founder_id=user.id, amount_lkr=amount, status="paid", provider="demo", reference=f"DEMO-{booking.id[:8]}")
        session.add(payment)
    else: payment.status = "paid"
    session.add(Notification(user_id=booking.advisor_id, notification_type=NotificationType.SYSTEM, title="Consultation payment recorded", body=f"Payment was recorded for: {booking.topic}", payload={"booking_request_id": booking.id}))
    session.commit(); session.refresh(payment)
    return APIResponse(data=BookingPaymentResponse.model_validate(payment), message="Demonstration payment recorded. No money was charged.")


@router.get("/booking-requests/{request_id}/payment", response_model=APIResponse[BookingPaymentResponse | None])
def booking_payment(request_id: str, user: CurrentUser, session: DatabaseSession) -> APIResponse[BookingPaymentResponse | None]:
    booking = session.get(AdvisorBookingRequest, request_id)
    if not booking or user.id not in {booking.founder_id, booking.advisor_id}:
        raise ResourceNotFoundError("Booking was not found.")
    payment = session.scalar(select(AdvisorBookingPayment).where(AdvisorBookingPayment.booking_request_id == booking.id))
    return APIResponse(data=BookingPaymentResponse.model_validate(payment) if payment else None)


def advisor_response(user: User, profile: AdvisorProfile | None) -> HumanAdvisorResponse:
    is_legal = user.role == UserRole.LEGAL_ADVISOR
    return HumanAdvisorResponse(
        id=user.id,
        full_name=user.full_name,
        role="Legal advisor" if is_legal else "Business mentor",
        specialisation=profile.specialisation if profile else ("Business registration, licences, and compliance" if is_legal else "Startup validation, growth, and operations"),
        consultation_modes=["online", "in_person"],
        verification_status="Verified platform advisor" if profile else "Platform role assigned",
        photo_url=profile.photo_url if profile else None,
        bio=profile.bio if profile else None,
        languages=profile.languages or [] if profile else [],
        consultation_fee=float(profile.consultation_fee) if profile and profile.consultation_fee is not None else None,
        availability=profile.availability or [] if profile else [],
        professional_body=profile.professional_body if profile else None,
        qualifications=profile.qualifications if profile else None,
        registration_details=profile.registration_details if profile else None,
        membership_plan=profile.membership_plan if profile else "general",
        office_address=profile.office_address if profile else None,
        service_fees=profile.service_fees or [] if profile else [],
    )


def advisor_profile_or_none(session: DatabaseSession, user_id: str) -> AdvisorProfile | None:
    """Keep the public directory usable while an older development database is upgraded."""
    try:
        return session.scalar(select(AdvisorProfile).where(AdvisorProfile.user_id == user_id, AdvisorProfile.is_visible.is_(True)))
    except SQLAlchemyError:
        session.rollback()
        return None


def _require_advisor(user: User) -> None:
    if user.role not in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
        raise ResourceNotFoundError("Advisor workspace is not available for this account.")


@router.get("/profile/me", response_model=APIResponse[HumanAdvisorResponse])
def my_advisor_profile(user: CurrentUser, session: DatabaseSession) -> APIResponse[HumanAdvisorResponse]:
    _require_advisor(user)
    return APIResponse(data=advisor_response(user, advisor_profile_or_none(session, user.id)))


@router.put("/profile/me", response_model=APIResponse[HumanAdvisorResponse])
def update_my_advisor_profile(payload: AdvisorProfileUpdate, user: CurrentUser, session: DatabaseSession) -> APIResponse[HumanAdvisorResponse]:
    _require_advisor(user)
    profile = session.scalar(select(AdvisorProfile).where(AdvisorProfile.user_id == user.id))
    if not profile:
        profile = AdvisorProfile(user_id=user.id, specialisation=payload.specialisation)
        session.add(profile)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    admins = session.scalars(select(User).where(User.role == UserRole.ADMIN, User.is_active.is_(True))).all()
    for admin in admins:
        session.add(Notification(user_id=admin.id, notification_type=NotificationType.SYSTEM, title="Advisor profile updated", body=f"{user.full_name} updated professional profile details for review.", payload={"advisor_id": user.id, "path": "/admin"}))
    session.commit(); session.refresh(profile)
    return APIResponse(data=advisor_response(user, profile), message="Profile saved. Administrators were notified to review public-profile changes.")


@router.get("", response_model=APIResponse[list[HumanAdvisorResponse]])
def list_advisors(session: DatabaseSession, _: CurrentUser) -> APIResponse[list[HumanAdvisorResponse]]:
    users = session.scalars(select(User).where(User.role.in_([UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR]), User.is_active.is_(True)).order_by(User.full_name)).all()
    return APIResponse(data=[advisor_response(user, advisor_profile_or_none(session, user.id)) for user in users])


@router.get("/{advisor_id}/available-slots", response_model=APIResponse[list[AvailabilitySlotResponse]])
def available_slots(advisor_id: str, session: DatabaseSession, _: CurrentUser) -> APIResponse[list[AvailabilitySlotResponse]]:
    return APIResponse(data=list(session.scalars(select(AdvisorAvailabilitySlot).where(AdvisorAvailabilitySlot.advisor_id == advisor_id, AdvisorAvailabilitySlot.is_booked.is_(False)).order_by(AdvisorAvailabilitySlot.starts_at).limit(50))))


@router.post("/availability-slots", response_model=APIResponse[AvailabilitySlotResponse])
def create_availability_slot(payload: AvailabilitySlotCreate, user: CurrentUser, session: DatabaseSession) -> APIResponse[AvailabilitySlotResponse]:
    if user.role not in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}: raise ResourceNotFoundError("Advisor workspace is not available for this account.")
    if payload.ends_at <= payload.starts_at: raise ResourceNotFoundError("The availability end time must be after the start time.")
    slot = AdvisorAvailabilitySlot(advisor_id=user.id, **payload.model_dump())
    session.add(slot); session.commit(); session.refresh(slot)
    return APIResponse(data=AvailabilitySlotResponse.model_validate(slot), message="Availability slot created.")


@router.get("/availability-slots/mine", response_model=APIResponse[list[AvailabilitySlotResponse]])
def my_availability_slots(user: CurrentUser, session: DatabaseSession) -> APIResponse[list[AvailabilitySlotResponse]]:
    if user.role not in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}: raise ResourceNotFoundError("Advisor workspace is not available for this account.")
    return APIResponse(data=list(session.scalars(select(AdvisorAvailabilitySlot).where(AdvisorAvailabilitySlot.advisor_id == user.id).order_by(AdvisorAvailabilitySlot.starts_at))))


@router.delete("/availability-slots/{slot_id}", response_model=APIResponse[None])
def delete_availability_slot(slot_id: str, user: CurrentUser, session: DatabaseSession) -> APIResponse[None]:
    slot = session.get(AdvisorAvailabilitySlot, slot_id)
    if not slot or slot.advisor_id != user.id or slot.is_booked: raise ResourceNotFoundError("This available slot was not found or cannot be removed.")
    session.delete(slot); session.commit()
    return APIResponse(data=None, message="Availability slot removed.")


@router.post("/booking-requests", response_model=APIResponse[BookingRequestResponse])
def create_booking(payload: BookingRequestCreate, user: CurrentUser, session: DatabaseSession) -> APIResponse[BookingRequestResponse]:
    advisor = session.get(User, payload.advisor_id)
    if not advisor or not advisor.is_active or advisor.role not in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
        raise ResourceNotFoundError("Advisor was not found.")

    # Booking submission is intentionally idempotent. A slow network response can
    # otherwise lead a founder to click the confirmation button twice and create
    # several identical consultation requests (for example, multiple TIN requests).
    existing_request = session.scalar(
        select(AdvisorBookingRequest)
        .where(
            AdvisorBookingRequest.founder_id == user.id,
            AdvisorBookingRequest.advisor_id == advisor.id,
            AdvisorBookingRequest.topic == payload.topic.strip(),
            AdvisorBookingRequest.status.in_(("pending", "accepted")),
        )
        .order_by(AdvisorBookingRequest.created_at.desc())
    )
    if existing_request:
        return APIResponse(
            data=BookingRequestResponse.model_validate(existing_request),
            message="Your existing active consultation request was kept; no duplicate booking was created.",
        )

    slot = session.get(AdvisorAvailabilitySlot, payload.availability_slot_id) if payload.availability_slot_id else None
    if slot and (slot.advisor_id != advisor.id or slot.is_booked or slot.consultation_type != payload.consultation_type): raise ResourceNotFoundError("The selected appointment slot is no longer available.")
    profile = advisor_profile_or_none(session, advisor.id)
    services = profile.service_fees or [] if profile else []
    selected_service = next((service for service in services if str(service.get("name", "")).strip() == (payload.service_name or "").strip()), None)
    service_name = str(selected_service.get("name")) if selected_service else (payload.service_name or "General consultation")
    quoted_fee = float(selected_service.get("fee_lkr", 0)) if selected_service else (float(profile.consultation_fee) if profile and profile.consultation_fee is not None else 0.0)
    request = AdvisorBookingRequest(founder_id=user.id, advisor_id=advisor.id, consultation_type=payload.consultation_type, topic=payload.topic, message=payload.message, availability_slot_id=slot.id if slot else None, scheduled_at=slot.starts_at if slot else None, service_name=service_name, quoted_fee_lkr=quoted_fee)
    if slot: slot.is_booked = True
    session.add(Notification(user_id=advisor.id, notification_type=NotificationType.SYSTEM, title="New consultation request", body=f"{user.full_name} requested a consultation about: {payload.topic}", payload={"booking_request_id": request.id, "path": "/advisor-dashboard"}))
    session.add(request); session.commit(); session.refresh(request)
    return APIResponse(data=BookingRequestResponse.model_validate(request), message="Consultation request sent.")


@router.get("/booking-requests/mine", response_model=APIResponse[list[FounderBookingResponse]])
def founder_bookings(user: CurrentUser, session: DatabaseSession) -> APIResponse[list[FounderBookingResponse]]:
    requests = session.scalars(select(AdvisorBookingRequest).where(AdvisorBookingRequest.founder_id == user.id).order_by(AdvisorBookingRequest.created_at.desc())).all()
    results: list[FounderBookingResponse] = []
    for request in requests:
        advisor = session.get(User, request.advisor_id)
        results.append(FounderBookingResponse(id=request.id, advisor_id=request.advisor_id, consultation_type=request.consultation_type, topic=request.topic, message=request.message, status=request.status, advisor_note=request.advisor_note, scheduled_at=request.scheduled_at, created_at=request.created_at, meeting_url=request.meeting_url, availability_slot_id=request.availability_slot_id, service_name=request.service_name, quoted_fee_lkr=float(request.quoted_fee_lkr), advisor_name=advisor.full_name if advisor else "Advisor", advisor_role="Legal advisor" if advisor and advisor.role == UserRole.LEGAL_ADVISOR else "Business mentor"))
    return APIResponse(data=results)


@router.get("/booking-requests/incoming", response_model=APIResponse[list[IncomingBookingResponse]])
def incoming_bookings(user: CurrentUser, session: DatabaseSession) -> APIResponse[list[IncomingBookingResponse]]:
    if user.role not in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
        raise ResourceNotFoundError("Advisor workspace is not available for this account.")
    requests = session.scalars(select(AdvisorBookingRequest).where(AdvisorBookingRequest.advisor_id == user.id).order_by(AdvisorBookingRequest.created_at.desc())).all()
    results: list[IncomingBookingResponse] = []
    for request in requests:
        founder = session.get(User, request.founder_id)
        results.append(IncomingBookingResponse(id=request.id, advisor_id=request.advisor_id, consultation_type=request.consultation_type, topic=request.topic, message=request.message, status=request.status, advisor_note=request.advisor_note, scheduled_at=request.scheduled_at, created_at=request.created_at, meeting_url=request.meeting_url, availability_slot_id=request.availability_slot_id, service_name=request.service_name, quoted_fee_lkr=float(request.quoted_fee_lkr), founder_name=founder.full_name if founder else "Founder account", founder_email=founder.email if founder else ""))
    return APIResponse(data=results)


@router.patch("/booking-requests/{request_id}", response_model=APIResponse[BookingRequestResponse])
def update_booking(request_id: str, payload: BookingRequestUpdate, user: CurrentUser, session: DatabaseSession) -> APIResponse[BookingRequestResponse]:
    if user.role not in {UserRole.LEGAL_ADVISOR, UserRole.BUSINESS_MENTOR}:
        raise ResourceNotFoundError("Advisor workspace is not available for this account.")
    request = session.get(AdvisorBookingRequest, request_id)
    if not request or request.advisor_id != user.id:
        raise ResourceNotFoundError("Consultation request was not found.")
    request.status = payload.status; request.advisor_note = payload.advisor_note; request.scheduled_at = payload.scheduled_at or request.scheduled_at; request.meeting_url = payload.meeting_url
    if payload.status in {"declined", "cancelled"} and request.availability_slot_id:
        slot = session.get(AdvisorAvailabilitySlot, request.availability_slot_id)
        if slot: slot.is_booked = False
    session.add(Notification(user_id=request.founder_id, notification_type=NotificationType.SYSTEM, title=f"Consultation {payload.status}", body=f"Your consultation about '{request.topic}' was {payload.status} by your advisor.", payload={"booking_request_id": request.id, "meeting_url": request.meeting_url, "scheduled_at": request.scheduled_at.isoformat() if request.scheduled_at else None, "path": "/dashboard"}))
    session.commit(); session.refresh(request)
    return APIResponse(data=BookingRequestResponse.model_validate(request), message="Consultation request updated.")


def _booking_for_participant(request_id: str, user: User, session: DatabaseSession) -> AdvisorBookingRequest:
    booking = session.get(AdvisorBookingRequest, request_id)
    if not booking or user.id not in {booking.founder_id, booking.advisor_id}:
        raise ResourceNotFoundError("Consultation request was not found.")
    return booking


@router.get("/booking-requests/{request_id}/messages", response_model=APIResponse[list[BookingMessageResponse]])
def list_booking_messages(request_id: str, user: CurrentUser, session: DatabaseSession) -> APIResponse[list[BookingMessageResponse]]:
    _booking_for_participant(request_id, user, session)
    items = session.scalars(select(AdvisorBookingMessage).where(AdvisorBookingMessage.booking_request_id == request_id).order_by(AdvisorBookingMessage.created_at)).all()
    return APIResponse(data=[BookingMessageResponse(id=item.id, booking_request_id=item.booking_request_id, sender_id=item.sender_id, sender_name=(session.get(User, item.sender_id).full_name if session.get(User, item.sender_id) else "Account"), body=item.body, created_at=item.created_at) for item in items])


@router.post("/booking-requests/{request_id}/messages", response_model=APIResponse[BookingMessageResponse])
def create_booking_message(request_id: str, payload: BookingMessageCreate, user: CurrentUser, session: DatabaseSession) -> APIResponse[BookingMessageResponse]:
    booking = _booking_for_participant(request_id, user, session)
    item = AdvisorBookingMessage(booking_request_id=booking.id, sender_id=user.id, body=payload.body.strip())
    recipient_id = booking.advisor_id if user.id == booking.founder_id else booking.founder_id
    session.add(item)
    session.add(Notification(user_id=recipient_id, notification_type=NotificationType.SYSTEM, title="New consultation message", body=f"You received a message about: {booking.topic}", payload={"booking_request_id": booking.id, "path": "/advisor-dashboard" if recipient_id == booking.advisor_id else "/dashboard"}))
    session.commit(); session.refresh(item)
    return APIResponse(data=BookingMessageResponse(id=item.id, booking_request_id=item.booking_request_id, sender_id=item.sender_id, sender_name=user.full_name, body=item.body, created_at=item.created_at), message="Message sent.")


def _document_response(item: AdvisorDocumentRequest, session: DatabaseSession) -> DocumentRequestResponse:
    documents = session.scalars(select(AdvisorSharedDocument).where(AdvisorSharedDocument.document_request_id == item.id).order_by(AdvisorSharedDocument.created_at.desc())).all()
    return DocumentRequestResponse(id=item.id, booking_request_id=item.booking_request_id, title=item.title, instructions=item.instructions, status=item.status, created_at=item.created_at, documents=[SharedDocumentResponse.model_validate(document) for document in documents])


@router.get("/booking-requests/{request_id}/document-requests", response_model=APIResponse[list[DocumentRequestResponse]])
def list_document_requests(request_id: str, user: CurrentUser, session: DatabaseSession) -> APIResponse[list[DocumentRequestResponse]]:
    _booking_for_participant(request_id, user, session)
    items = session.scalars(select(AdvisorDocumentRequest).where(AdvisorDocumentRequest.booking_request_id == request_id).order_by(AdvisorDocumentRequest.created_at.desc())).all()
    return APIResponse(data=[_document_response(item, session) for item in items])


@router.post("/booking-requests/{request_id}/document-requests", response_model=APIResponse[DocumentRequestResponse])
def create_document_request(request_id: str, payload: DocumentRequestCreate, user: CurrentUser, session: DatabaseSession) -> APIResponse[DocumentRequestResponse]:
    booking = _booking_for_participant(request_id, user, session)
    if booking.advisor_id != user.id:
        raise ResourceNotFoundError("Only the assigned advisor can request documents.")
    item = AdvisorDocumentRequest(booking_request_id=booking.id, advisor_id=user.id, founder_id=booking.founder_id, title=payload.title.strip(), instructions=payload.instructions)
    session.add(item)
    session.add(Notification(user_id=booking.founder_id, notification_type=NotificationType.SYSTEM, title="Advisor requested a document", body=f"{user.full_name} requested: {item.title}", payload={"booking_request_id": booking.id, "path": "/dashboard"}))
    session.commit(); session.refresh(item)
    return APIResponse(data=_document_response(item, session), message="Document request sent to founder.")


@router.post("/document-requests/{document_request_id}/upload", response_model=APIResponse[SharedDocumentResponse])
async def upload_shared_document(document_request_id: str, user: CurrentUser, session: DatabaseSession, document: UploadFile = File(...)) -> APIResponse[SharedDocumentResponse]:
    request = session.get(AdvisorDocumentRequest, document_request_id)
    if not request or request.founder_id != user.id:
        raise ResourceNotFoundError("Document request was not found.")
    stored = await BookingDocumentService(session).upload(request.id, user.id, document)
    request.status = "submitted"
    session.add(Notification(user_id=request.advisor_id, notification_type=NotificationType.SYSTEM, title="Founder shared a requested document", body=f"A document was uploaded for: {request.title}", payload={"booking_request_id": request.booking_request_id, "document_request_id": request.id, "path": "/advisor-dashboard"}))
    session.commit(); session.refresh(stored)
    return APIResponse(data=SharedDocumentResponse.model_validate(stored), message="Document stored securely for the assigned advisor.")


@router.get("/shared-documents/{document_id}")
def read_shared_document(document_id: str, user: CurrentUser, session: DatabaseSession) -> Response:
    document = session.get(AdvisorSharedDocument, document_id)
    if not document:
        raise ResourceNotFoundError("Shared document was not found.")
    request = session.get(AdvisorDocumentRequest, document.document_request_id)
    if not request or user.id not in {request.founder_id, request.advisor_id}:
        raise ResourceNotFoundError("Shared document was not found.")
    if user.id == request.advisor_id:
        document.reviewed = True; request.status = "reviewed"; session.commit()
    raw = BookingDocumentService(session).read(document)
    return Response(content=raw, media_type=document.content_type, headers={"Content-Disposition": f'inline; filename="{document.original_name.replace(chr(34), "")}"', "Cache-Control": "no-store"})
