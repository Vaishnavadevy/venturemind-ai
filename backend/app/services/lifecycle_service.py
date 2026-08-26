"""Owner-scoped startup lifecycle workspace use cases."""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ai.lifecycle_risk_engine import LifecycleRiskEngine
from app.services.explainable_ai_service import ExplainableAIService
from app.core.exceptions import VentureMindError
from app.models.lifecycle import LifecycleMilestone, LifecycleRiskAssessment, Organization, OrganizationMember, StartupProfile
from app.models.user import User
from app.schemas.lifecycle import StartupProfileUpsert

DEFAULT_MILESTONES = [
    ("idea_created", "Idea Created"), ("risk_analysis", "Risk Analysis Completed"),
    ("business_registered", "Business Registered"), ("tax_registered", "Tax Registered"),
    ("licenses_approved", "Licences Approved"), ("brand_created", "Brand Identity Created"),
    ("website_created", "Website Created"), ("employees_hired", "Employees Hired"),
    ("marketing_started", "Marketing Started"), ("business_opened", "Business Opened"),
    ("requirements_completed", "Business Requirements Completed"),
]

logger = logging.getLogger(__name__)


class LifecycleService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _profile(self, user: User, profile_id: str) -> StartupProfile:
        profile = self.session.get(StartupProfile, profile_id)
        if not profile or profile.created_by_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup profile not found.")
        return profile

    def create_profile(self, user: User, payload: StartupProfileUpsert) -> StartupProfile:
        organization = Organization(owner_id=user.id, name=payload.business_name, country=payload.country)
        self.session.add(organization)
        self.session.flush()
        profile = StartupProfile(organization_id=organization.id, created_by_id=user.id, **payload.model_dump())
        self.session.add(profile)
        self.session.flush()
        self.session.add(OrganizationMember(organization_id=organization.id, user_id=user.id, member_role="founder"))
        self.session.add_all([LifecycleMilestone(startup_profile_id=profile.id, milestone_key=key, title=title) for key, title in DEFAULT_MILESTONES])
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def list_profiles(self, user: User) -> list[StartupProfile]:
        return list(self.session.scalars(select(StartupProfile).where(StartupProfile.created_by_id == user.id).order_by(StartupProfile.updated_at.desc())))

    def update_profile(self, user: User, profile_id: str, payload: StartupProfileUpsert) -> StartupProfile:
        profile = self._profile(user, profile_id)
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def milestones(self, user: User, profile_id: str) -> list[LifecycleMilestone]:
        self._profile(user, profile_id)
        return list(self.session.scalars(select(LifecycleMilestone).where(LifecycleMilestone.startup_profile_id == profile_id).order_by(LifecycleMilestone.created_at)))

    def set_milestone(self, user: User, profile_id: str, milestone_key: str, completed: bool) -> LifecycleMilestone:
        self._profile(user, profile_id)
        milestone = self.session.scalar(select(LifecycleMilestone).where(LifecycleMilestone.startup_profile_id == profile_id, LifecycleMilestone.milestone_key == milestone_key))
        if not milestone:
            titles = dict(DEFAULT_MILESTONES)
            if milestone_key not in titles:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lifecycle milestone not found.")
            milestone = LifecycleMilestone(startup_profile_id=profile_id, milestone_key=milestone_key, title=titles[milestone_key])
            self.session.add(milestone)
        milestone.completed_at = datetime.now(timezone.utc) if completed else None
        self.session.commit()
        self.session.refresh(milestone)
        return milestone

    def assess_risk(self, user: User, profile_id: str) -> LifecycleRiskAssessment:
        profile = self._profile(user, profile_id)
        engine = LifecycleRiskEngine()
        scores = engine.evaluate(profile)
        success, confidence, overall_risk, level = engine.summary(scores)
        scorecards = [{"key": score.key, "label": score.label, "risk_score": score.risk_score, "reasoning": score.reasoning, "positive_factors": score.positive_factors, "negative_factors": score.negative_factors, "suggestions": score.suggestions} for score in scores]
        weakest = sorted(scores, key=lambda score: score.risk_score, reverse=True)[:3]
        recommendations = [{"priority": "high" if index == 0 else "medium", "metric": score.key, "recommendation": score.suggestions[0]} for index, score in enumerate(weakest)]
        ai_explanation = ExplainableAIService().explain(profile, scores)
        try:
            assessment = self.session.scalar(
                select(LifecycleRiskAssessment)
                .where(LifecycleRiskAssessment.startup_profile_id == profile.id)
                .order_by(LifecycleRiskAssessment.created_at.desc())
            )
            if assessment is None:
                assessment = LifecycleRiskAssessment(
                    startup_profile_id=profile.id,
                    overall_success_score=success,
                    business_confidence_score=confidence,
                    overall_risk_score=overall_risk,
                    risk_level=level,
                    methodology_version="lifecycle-risk-v1",
                    scorecards=scorecards,
                    recommendations=recommendations,
                    ai_explanation=ai_explanation,
                )
                self.session.add(assessment)
            else:
                assessment.overall_success_score = success
                assessment.business_confidence_score = confidence
                assessment.overall_risk_score = overall_risk
                assessment.risk_level = level
                assessment.methodology_version = "lifecycle-risk-v1"
                assessment.scorecards = scorecards
                assessment.recommendations = recommendations
                assessment.ai_explanation = ai_explanation
            self.session.commit()
            self.session.refresh(assessment)
            return assessment
        except SQLAlchemyError as exc:
            self.session.rollback()
            logger.exception("Could not persist lifecycle risk assessment for profile %s", profile.id)
            raise VentureMindError("Risk analysis could not be saved. Verify the lifecycle risk-assessment database migration and retry.") from exc

    def latest_risk_assessment(self, user: User, profile_id: str) -> LifecycleRiskAssessment:
        self._profile(user, profile_id)
        assessment = self.session.scalar(select(LifecycleRiskAssessment).where(LifecycleRiskAssessment.startup_profile_id == profile_id).order_by(LifecycleRiskAssessment.created_at.desc()))
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No risk assessment exists for this startup profile.")
        return assessment
