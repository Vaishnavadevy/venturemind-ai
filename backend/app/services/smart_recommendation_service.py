"""Generate transparent founder recommendations from saved VentureMind records."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.lifecycle import LifecycleFinancialPlan, LifecycleMilestone, LifecycleRiskAssessment, StartupProfile
from app.models.operations import Employee, OperationTask
from app.models.smart_recommendation import SmartRecommendationState
from app.models.user import User
from app.schemas.smart_recommendations import SmartRecommendationResponse, SmartRecommendationSnapshot


class SmartRecommendationService:
    """Uses only persisted profile/lifecycle/operations evidence; it never invents data."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def current(self, user: User) -> SmartRecommendationSnapshot:
        profile = self.session.scalar(
            select(StartupProfile)
            .where(StartupProfile.created_by_id == user.id)
            .order_by(StartupProfile.updated_at.desc())
        )
        if not profile:
            return SmartRecommendationSnapshot(
                generated_from=["No saved startup profile is available yet."], recommendations=[]
            )

        risk = self.session.scalar(
            select(LifecycleRiskAssessment)
            .where(LifecycleRiskAssessment.startup_profile_id == profile.id)
            .order_by(LifecycleRiskAssessment.created_at.desc())
        )
        finance = self.session.scalar(
            select(LifecycleFinancialPlan)
            .where(LifecycleFinancialPlan.startup_profile_id == profile.id)
            .order_by(LifecycleFinancialPlan.created_at.desc())
        )
        requirements_complete = bool(self.session.scalar(
            select(LifecycleMilestone.id).where(
                LifecycleMilestone.startup_profile_id == profile.id,
                LifecycleMilestone.milestone_key == "requirements_completed",
                LifecycleMilestone.completed_at.is_not(None),
            )
        ))
        employee_count = int(self.session.scalar(
            select(func.count()).select_from(Employee).where(Employee.startup_profile_id == profile.id)
        ) or 0)
        open_task_count = int(self.session.scalar(
            select(func.count()).select_from(OperationTask).where(
                OperationTask.startup_profile_id == profile.id,
                OperationTask.status != "done",
            )
        ) or 0)
        states = {
            state.recommendation_key: state
            for state in self.session.scalars(
                select(SmartRecommendationState).where(SmartRecommendationState.startup_profile_id == profile.id)
            )
        }
        recommendations: list[dict[str, str]] = []
        required = {
            "business name": profile.business_name,
            "business category": profile.category,
            "business description": profile.description,
            "target customers": profile.target_customers,
            "country": profile.country,
            "city": profile.city,
            "available budget": profile.available_budget,
            "launch timeline": profile.launch_timeline,
        }
        missing = [label for label, value in required.items() if value in (None, "")]
        if missing:
            recommendations.append({
                "key": "complete_startup_profile", "title": "Complete your startup profile",
                "reason": f"Missing saved information: {', '.join(missing)}.", "priority": "High",
                "related_module": "Startup Workspace", "action_label": "Complete profile", "action_path": "/workspace#startup-profile",
            })
        if not risk:
            recommendations.append({
                "key": "run_risk_analysis", "title": "Run your evidence-based risk analysis",
                "reason": "No saved risk assessment exists for this startup profile.", "priority": "High",
                "related_module": "Risk Analysis", "action_label": "Run analysis", "action_path": "/workspace#risk-analysis",
            })
        if not finance:
            recommendations.append({
                "key": "complete_financial_plan", "title": "Complete your financial plan",
                "reason": "No saved financial plan exists, so break-even and cash-flow assumptions cannot be reviewed.", "priority": "High",
                "related_module": "Financial Planning", "action_label": "Open financial plan", "action_path": "/workspace#financial-plan",
            })
        if not requirements_complete:
            recommendations.append({
                "key": "complete_business_requirements", "title": "Complete the business setup requirements",
                "reason": "The business requirements milestone is not marked complete.", "priority": "Medium",
                "related_module": "Business Requirements", "action_label": "Open checklist", "action_path": "/workspace#business-requirements",
            })
        if profile.expected_employees > 0 and employee_count == 0:
            recommendations.append({
                "key": "add_planned_employees", "title": "Add your planned employees",
                "reason": f"Your profile plans for {profile.expected_employees} employee(s), but no employee record is saved.", "priority": "Medium",
                "related_module": "Business Operations", "action_label": "Open operations", "action_path": "/operations",
            })
        if open_task_count == 0 and profile.status != "draft":
            recommendations.append({
                "key": "create_first_operation_task", "title": "Create your first operating task",
                "reason": "No open task is saved for this startup profile.", "priority": "Low",
                "related_module": "Business Operations", "action_label": "Create task", "action_path": "/operations",
            })
        if risk and risk.scorecards:
            highest = max(risk.scorecards, key=lambda item: float(item.get("risk_score", 0)))
            label = str(highest.get("label", "priority risk"))
            score = round(float(highest.get("risk_score", 0)))
            recommendations.append({
                "key": f"review_{str(highest.get('key', 'priority_risk'))}", "title": f"Reduce {label.lower()}",
                "reason": f"The latest saved assessment rates {label.lower()} at {score}/100.", "priority": "High" if score >= 70 else "Medium",
                "related_module": "Risk Analysis", "action_label": "View risk analysis", "action_path": "/workspace#risk-analysis",
            })

        result = []
        for item in recommendations[:5]:
            state = states.get(item["key"])
            result.append(SmartRecommendationResponse(
                id=state.id if state else None,
                **item,
                status=state.status if state else "open",
                completed_at=state.completed_at if state else None,
            ))
        return SmartRecommendationSnapshot(
            startup_profile_id=profile.id,
            generated_from=["Startup profile", "Risk analysis", "Financial plan", "Business requirements", "Tasks", "Employees"],
            recommendations=result,
        )

    def set_completed(self, user: User, recommendation_key: str, completed: bool) -> SmartRecommendationResponse:
        snapshot = self.current(user)
        item = next((entry for entry in snapshot.recommendations if entry.key == recommendation_key), None)
        if not item or not snapshot.startup_profile_id:
            raise ResourceNotFoundError("Smart recommendation was not found for your current startup profile.")
        state = self.session.scalar(select(SmartRecommendationState).where(
            SmartRecommendationState.startup_profile_id == snapshot.startup_profile_id,
            SmartRecommendationState.recommendation_key == recommendation_key,
        ))
        if not state:
            state = SmartRecommendationState(
                startup_profile_id=snapshot.startup_profile_id,
                recommendation_key=recommendation_key,
            )
            self.session.add(state)
        state.status = "completed" if completed else "open"
        state.completed_at = datetime.utcnow() if completed else None
        self.session.commit()
        self.session.refresh(state)
        return item.model_copy(update={"id": state.id, "status": state.status, "completed_at": state.completed_at})
