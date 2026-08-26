"""Educational company-registration guide endpoints."""

from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.business_registration import RegistrationItemUpdate, RegistrationJourneyResponse, RegistrationJourneyStart, RegistrationJourneyUpdate
from app.schemas.common import APIResponse
from app.services.business_registration_service import BusinessRegistrationService

router = APIRouter(prefix="/business-registration")


@router.get("/current", response_model=APIResponse[RegistrationJourneyResponse])
def current(user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=BusinessRegistrationService(session).current(user))


@router.post("/start", response_model=APIResponse[RegistrationJourneyResponse])
def start(payload: RegistrationJourneyStart, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=BusinessRegistrationService(session).start(user, payload.mode))


@router.patch("/current", response_model=APIResponse[RegistrationJourneyResponse])
def update(payload: RegistrationJourneyUpdate, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=BusinessRegistrationService(session).update(user, payload.company_type, payload.proposed_company_name))


@router.patch("/items/{item_id}", response_model=APIResponse[RegistrationJourneyResponse])
def update_item(item_id: str, payload: RegistrationItemUpdate, user: CurrentUser, session: DatabaseSession):
    return APIResponse(data=BusinessRegistrationService(session).update_item(user, item_id, payload.status))
