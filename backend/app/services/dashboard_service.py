"""Owner-scoped aggregation for the founder dashboard."""

from collections import defaultdict
from decimal import Decimal

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, selectinload

from app.models.evaluation import Evaluation
from app.models.business_registration import BusinessRegistrationChecklistItem, BusinessRegistrationJourney
from app.models.lifecycle import LifecycleFinancialPlan, LifecycleMilestone, LifecycleRiskAssessment, StartupProfile
from app.models.project import Project, StartupIdea
from app.models.report import Report
from app.models.user import User
from app.schemas.dashboard import DashboardJourney, DashboardMetric, DashboardProject, DashboardReport, DashboardRisk, DashboardScore, DashboardSnapshot


def as_float(value: Decimal | float | None) -> float | None:
    return float(value) if value is not None else None


def title_for(metric_key: str) -> str:
    return metric_key.replace("_", " ").replace("risk resilience", "risk resilience").title()


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def snapshot(self, user: User) -> DashboardSnapshot:
        # Registration is an optional later-stage workflow. A partially migrated
        # development database must not prevent a founder from opening the core
        # dashboard, profile, risks, or AI Advisor.
        inspector = inspect(self.session.get_bind())
        registration_tables_ready = (
            inspector.has_table("business_registration_journeys")
            and inspector.has_table("business_registration_checklist_items")
        )
        profile = self.session.scalar(
            select(StartupProfile)
            .where(StartupProfile.created_by_id == user.id)
            .order_by(StartupProfile.updated_at.desc())
        )
        profile_required_fields = (
            profile.business_name,
            profile.category,
            profile.description,
            profile.target_customers,
            profile.country,
            profile.city or profile.district,
            profile.business_goals,
            profile.launch_timeline,
        ) if profile else ()
        profile_complete = bool(profile and all(value not in (None, "") for value in profile_required_fields))
        latest_lifecycle_risk = self.session.scalar(
            select(LifecycleRiskAssessment)
            .where(LifecycleRiskAssessment.startup_profile_id == profile.id)
            .order_by(LifecycleRiskAssessment.created_at.desc())
        ) if profile else None
        latest_financial_plan = self.session.scalar(
            select(LifecycleFinancialPlan)
            .where(LifecycleFinancialPlan.startup_profile_id == profile.id)
            .order_by(LifecycleFinancialPlan.created_at.desc())
        ) if profile else None
        registration = self.session.scalar(
            select(BusinessRegistrationJourney).where(BusinessRegistrationJourney.startup_profile_id == profile.id)
        ) if profile and registration_tables_ready else None
        registration_items = list(self.session.scalars(
            select(BusinessRegistrationChecklistItem).where(BusinessRegistrationChecklistItem.journey_id == registration.id)
        )) if registration else []
        registration_completed = sum(item.status in {"completed", "approved"} for item in registration_items)
        profile_total = len(profile_required_fields)
        profile_completed = sum(value not in (None, "") for value in profile_required_fields)
        financial_results = latest_financial_plan.results if latest_financial_plan else {}
        requirements_complete = bool(profile and self.session.scalar(
            select(LifecycleMilestone.id)
            .where(LifecycleMilestone.startup_profile_id == profile.id, LifecycleMilestone.milestone_key == "requirements_completed", LifecycleMilestone.completed_at.is_not(None))
        ))
        journey = DashboardJourney(
            profile_complete=profile_complete,
            risk_complete=bool(latest_lifecycle_risk),
            financial_plan_complete=bool(latest_financial_plan),
            requirements_complete=requirements_complete,
            profile_updated_at=profile.updated_at if profile else None,
            profile_id=profile.id if profile else None,
            project_name=profile.business_name if profile else None,
            profile_completion_percentage=round((profile_completed / profile_total) * 100) if profile_total else 0,
            risk_score=as_float(latest_lifecycle_risk.overall_risk_score) if latest_lifecycle_risk else None,
            monthly_profit=as_float(financial_results.get("monthly_profit")) if financial_results else None,
            cash_runway_months=as_float(financial_results.get("runway_months")) if financial_results else None,
            break_even_months=as_float(financial_results.get("break_even_months")) if financial_results else None,
            registration_progress_percentage=round((registration_completed / len(registration_items)) * 100) if registration_items else 0,
            registration_status=registration.overall_status if registration else None,
        )
        projects = list(self.session.scalars(select(Project).where(Project.owner_id == user.id).order_by(Project.updated_at.desc())))
        project_ids = [project.id for project in projects]
        if not project_ids:
            risk_value = as_float(latest_lifecycle_risk.business_confidence_score) if latest_lifecycle_risk else None
            return DashboardSnapshot(
                metrics=[
                    DashboardMetric(label="Active startup projects", value="1" if profile else "0", detail="Your saved startup profile" if profile else "Create your first startup profile"),
                    DashboardMetric(label="Latest confidence score", value=f"{round(risk_value)}%" if risk_value is not None else "—", detail="Based on your latest saved risk assessment" if risk_value is not None else "Complete a risk evaluation"),
                    DashboardMetric(label="Highest priority risk", value="Available" if latest_lifecycle_risk else "—", detail="Open your risk analysis to review prioritised actions" if latest_lifecycle_risk else "No risks identified yet"),
                    DashboardMetric(label="Reports generated", value="0", detail="Generate a report after evaluation"),
                ],
                projects=[], latest_project=None, score_breakdown=[], trend=[], risks=[], reports=[], journey=journey,
            )

        ideas = list(self.session.scalars(select(StartupIdea).where(StartupIdea.project_id.in_(project_ids)).order_by(StartupIdea.project_id, StartupIdea.version.desc())))
        latest_idea_by_project: dict[str, StartupIdea] = {}
        for idea in ideas:
            latest_idea_by_project.setdefault(idea.project_id, idea)

        evaluations = list(self.session.scalars(select(Evaluation).options(selectinload(Evaluation.scores)).where(Evaluation.project_id.in_(project_ids)).order_by(Evaluation.completed_at.desc(), Evaluation.created_at.desc())))
        latest_evaluation_by_project: dict[str, Evaluation] = {}
        for evaluation in evaluations:
            latest_evaluation_by_project.setdefault(evaluation.project_id, evaluation)

        summaries: list[DashboardProject] = []
        for project in projects:
            idea = latest_idea_by_project.get(project.id)
            evaluation = latest_evaluation_by_project.get(project.id)
            summaries.append(DashboardProject(
                id=project.id, name=project.name, industry=idea.industry if idea else "Not specified", stage=idea.development_stage.value if idea else "idea", status=evaluation.status.value if evaluation else project.status.value,
                score=as_float(evaluation.overall_confidence_score) if evaluation else None, evaluation_id=evaluation.id if evaluation else None, updated_at=project.updated_at,
            ))

        latest = summaries[0] if summaries else None
        latest_evaluation = latest_evaluation_by_project.get(latest.id) if latest else None
        completed_scores = [float(item.overall_confidence_score) for item in evaluations if item.overall_confidence_score is not None]
        reports = list(self.session.scalars(select(Report).where(Report.project_id.in_(project_ids)).order_by(Report.generated_at.desc(), Report.created_at.desc()).limit(3)))

        score_breakdown = [DashboardScore(metric=title_for(score.metric_key), score=float(score.score)) for score in (latest_evaluation.scores if latest_evaluation else [])]
        trend = [DashboardScore(metric=item.completed_at.strftime("%d %b") if item.completed_at else item.created_at.strftime("%d %b"), score=float(item.overall_confidence_score)) for item in reversed([item for item in evaluations if item.overall_confidence_score is not None][:6])]
        # Prefer the saved lifecycle risk assessment because it is calculated from
        # the founder's current profile. The older evaluation data remains useful
        # for confidence history and reports, but must not contradict current risks.
        if latest_lifecycle_risk and latest_lifecycle_risk.scorecards:
            priority_cards = sorted(
                latest_lifecycle_risk.scorecards,
                key=lambda item: float(item.get("risk_score", 0)),
                reverse=True,
            )[:3]
            risks = [
                DashboardRisk(
                    label=str(item.get("label", "Business risk")),
                    level="High" if float(item.get("risk_score", 0)) >= 70 else "Moderate" if float(item.get("risk_score", 0)) >= 40 else "Low",
                    score=float(item.get("risk_score", 0)),
                    detail=(item.get("suggestions") or ["Review the supporting evidence before committing resources."])[0],
                )
                for item in priority_cards
            ]
        else:
            weakest = sorted(latest_evaluation.scores, key=lambda item: float(item.score))[:3] if latest_evaluation else []
            risks = [DashboardRisk(label=title_for(item.metric_key), level="High" if float(item.score) < 50 else "Moderate" if float(item.score) < 75 else "Low", score=float(item.score), detail=(item.improvement_suggestions[0] if item.improvement_suggestions else "Keep validating this area.")) for item in weakest]

        def report_name(report: Report) -> str:
            # UUID filenames are implementation details; never expose them as the report title.
            if not report.file_name or report.file_name.startswith("venturemind-"):
                return f"{report.project.name} evaluation report.pdf"
            return report.file_name

        priority_risk = risks[0] if risks else None
        return DashboardSnapshot(
            metrics=[
                DashboardMetric(label="Active startup projects", value=str(len(summaries)), detail="Saved to your account"),
                DashboardMetric(label="Latest confidence score", value=f"{round(latest.score)}%" if latest and latest.score is not None else "—", detail="Based on your latest saved evaluation"),
                DashboardMetric(label="Highest priority risk", value=priority_risk.label if priority_risk else "—", detail=priority_risk.detail if priority_risk else "Run an evaluation to identify focus areas"),
                DashboardMetric(label="Reports generated", value=str(len(reports)), detail="Most recent reports shown below"),
            ],
            projects=summaries[:5], latest_project=latest, score_breakdown=score_breakdown, trend=trend, risks=risks,
            reports=[DashboardReport(id=report.id, name=report_name(report), project_id=report.project_id, evaluation_id=report.evaluation_id, generated_at=report.generated_at, status=report.status.value) for report in reports], journey=journey,
        )
