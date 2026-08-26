"""Educational Sri Lankan company-registration guide; never submits to government systems."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.business_registration import BusinessRegistrationChecklistItem, BusinessRegistrationJourney
from app.models.lifecycle import StartupProfile
from app.models.user import User
from app.schemas.business_registration import RegistrationChecklistItemResponse, RegistrationJourneyResponse


OFFICIAL_DRC = "https://drc.gov.lk/en/"
ERO_C = "https://eroc.drc.gov.lk"
BO_PORTAL = "https://bo.drc.gov.lk"

STEPS = [
    ("company_type", 1, "Choose company type", "Understand the business structure you intend to use and confirm it with an appropriately qualified advisor if needed.", "Company type", OFFICIAL_DRC),
    ("company_name", 2, "Prepare company name", "Prepare an appropriate name and use the official name-search service before relying on its availability.", "Company name", "https://eroc.drc.gov.lk/home/search"),
    ("company_information", 3, "Prepare company information", "Collect the company address, contact details, director, shareholder, secretary, and ownership information required by the official process.", "Company information", OFFICIAL_DRC),
    ("required_documents", 4, "Prepare required documents", "Prepare identity and business documents requested by the official authority. VentureMind does not validate legal documents.", "Documents", OFFICIAL_DRC),
    ("application_preparation", 5, "Prepare application", "Review the official online application guidance and prepare accurate information before entering it into the government system.", "Application preparation", ERO_C),
    ("application_submission", 6, "Submit through official portal", "Use the official eROC portal to submit an application yourself. VentureMind never sends an application for you.", "Application submission", ERO_C),
    ("payment", 7, "Complete official payment", "Complete any official payment only on the government-authorised service and keep the receipt for your records.", "Payment", ERO_C),
    ("government_review", 8, "Track government review", "Check the application status through the official channel. Update this status manually because VentureMind is not connected to government systems.", "Review", ERO_C),
    ("registration_confirmation", 9, "Record registration confirmation", "After official approval, record the registration result and retain the official registration document.", "Confirmation", OFFICIAL_DRC),
    ("post_registration", 10, "Review post-registration duties", "Review tax, licences, annual compliance, and beneficial-ownership obligations with official sources or a qualified legal advisor.", "Post-registration", BO_PORTAL),
]

RESOURCES = [
    {"title": "Department of Registrar of Companies", "description": "Official Department of Registrar of Companies information and guidance.", "url": OFFICIAL_DRC, "category": "Official guidance", "official": True},
    {"title": "eROC registration portal", "description": "Official online service for company registration-related actions.", "url": ERO_C, "category": "Official portal", "official": True},
    {"title": "Official company name search", "description": "Use the government eROC name-search service before relying on a proposed company name.", "url": "https://eroc.drc.gov.lk/home/search", "category": "Name search", "official": True},
    {"title": "Beneficial Ownership portal", "description": "Official beneficial-ownership resource for applicable registered companies.", "url": BO_PORTAL, "category": "Post-registration", "official": True},
]


class BusinessRegistrationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _profile(self, user: User) -> StartupProfile:
        profile = self.session.scalar(select(StartupProfile).where(StartupProfile.created_by_id == user.id).order_by(StartupProfile.updated_at.desc()))
        if not profile:
            raise ResourceNotFoundError("Save a startup profile before starting the registration guide.")
        return profile

    def _journey(self, user: User) -> BusinessRegistrationJourney:
        profile = self._profile(user)
        journey = self.session.scalar(select(BusinessRegistrationJourney).where(BusinessRegistrationJourney.startup_profile_id == profile.id))
        if not journey:
            raise ResourceNotFoundError("Start the registration guide first.")
        return journey

    def _response(self, journey: BusinessRegistrationJourney) -> RegistrationJourneyResponse:
        items = list(self.session.scalars(select(BusinessRegistrationChecklistItem).where(BusinessRegistrationChecklistItem.journey_id == journey.id).order_by(BusinessRegistrationChecklistItem.step_number)))
        completed = sum(item.status in {"completed", "approved"} for item in items)
        journey.overall_status = "approved" if items and items[-1].status == "approved" else "in_progress" if any(item.status != "not_started" for item in items) else "not_started"
        self.session.commit()
        return RegistrationJourneyResponse(
            id=journey.id,
            startup_profile_id=journey.startup_profile_id,
            mode=journey.mode,
            company_type=journey.company_type,
            proposed_company_name=journey.proposed_company_name,
            overall_status=journey.overall_status,
            is_demo=journey.is_demo,
            progress_percentage=round((completed / len(items)) * 100) if items else 0,
            items=[RegistrationChecklistItemResponse.model_validate(item) for item in items],
            resources=RESOURCES,
        )

    def start(self, user: User, mode: str) -> RegistrationJourneyResponse:
        profile = self._profile(user)
        journey = self.session.scalar(select(BusinessRegistrationJourney).where(BusinessRegistrationJourney.startup_profile_id == profile.id))
        if not journey:
            journey = BusinessRegistrationJourney(startup_profile_id=profile.id, mode=mode, is_demo=mode == "demo", proposed_company_name=profile.business_name)
            self.session.add(journey)
            self.session.flush()
            for key, step, title, description, category, url in STEPS:
                self.session.add(BusinessRegistrationChecklistItem(journey_id=journey.id, item_key=key, step_number=step, title=title, description=description, category=category, official_url=url))
            self.session.commit()
        return self._response(journey)

    def current(self, user: User) -> RegistrationJourneyResponse:
        return self._response(self._journey(user))

    def update(self, user: User, company_type: str | None, proposed_company_name: str | None) -> RegistrationJourneyResponse:
        journey = self._journey(user)
        if company_type is not None:
            journey.company_type = company_type.strip() or None
        if proposed_company_name is not None:
            journey.proposed_company_name = proposed_company_name.strip() or None
        self.session.commit()
        return self._response(journey)

    def update_item(self, user: User, item_id: str, status: str) -> RegistrationJourneyResponse:
        journey = self._journey(user)
        item = self.session.get(BusinessRegistrationChecklistItem, item_id)
        if not item or item.journey_id != journey.id:
            raise ResourceNotFoundError("Registration checklist item was not found.")
        item.status = status
        item.completed_at = datetime.now(UTC) if status in {"completed", "approved"} else None
        self.session.commit()
        return self._response(journey)
