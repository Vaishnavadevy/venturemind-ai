"""API v1 router composition."""

from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.admin_management import router as admin_management_router
from app.api.v1.endpoints.human_advisors import router as human_advisors_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.competitors import router as competitors_router
from app.api.v1.endpoints.evaluations import router as evaluations_router
from app.api.v1.endpoints.financial_plans import router as financial_plans_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.lifecycle import router as lifecycle_router
from app.api.v1.endpoints.lifecycle_advisor import router as lifecycle_advisor_router
from app.api.v1.endpoints.projects import router as projects_router
from app.api.v1.endpoints.operations import router as operations_router
from app.api.v1.endpoints.platform_announcements import router as platform_announcements_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.smart_recommendations import router as smart_recommendations_router
from app.api.v1.endpoints.business_registration import router as business_registration_router
from app.api.v1.endpoints.public_advisor import router as public_advisor_router
from app.api.v1.endpoints.public_feedback import router as public_feedback_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["system"])
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(admin_router, tags=["admin"])
api_router.include_router(admin_management_router, tags=["admin management"])
api_router.include_router(human_advisors_router, tags=["human advisors"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(competitors_router, tags=["competitors"])
api_router.include_router(evaluations_router, tags=["evaluations"])
api_router.include_router(financial_plans_router, tags=["financial planning"])
api_router.include_router(projects_router, tags=["projects"])
api_router.include_router(operations_router, tags=["business operations"])
api_router.include_router(platform_announcements_router, tags=["platform announcements"])
api_router.include_router(lifecycle_router, tags=["startup lifecycle"])
api_router.include_router(lifecycle_advisor_router, tags=["AI business advisor"])
api_router.include_router(reports_router, tags=["reports"])
api_router.include_router(smart_recommendations_router, tags=["smart recommendations"])
api_router.include_router(business_registration_router, tags=["business registration"])
api_router.include_router(public_advisor_router, tags=["public local AI"])
api_router.include_router(public_feedback_router, tags=["public feedback"])
