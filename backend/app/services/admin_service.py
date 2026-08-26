"""Administrator management and aggregate analytics use cases."""

from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.enums import EvaluationStatus, FeedbackStatus, UserRole
from app.models.evaluation import Evaluation
from app.models.feedback import Feedback
from app.models.project import Project, StartupIdea
from app.models.report import Report
from app.models.user import User
from app.schemas.admin import (
    AdminAlertResponse,
    AnalyticsResponse,
    DistributionItem,
    PlatformInsightsResponse,
    TrendPoint,
)


class AdminService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def analytics(self) -> AnalyticsResponse:
        def count(model: type[object]) -> int:
            return self.session.scalar(select(func.count()).select_from(model)) or 0
        return AnalyticsResponse(
            total_users=count(User),
            active_users=self.session.scalar(
                select(func.count()).select_from(User).where(User.is_active.is_(True))
            )
            or 0,
            total_projects=count(Project),
            total_evaluations=count(Evaluation),
            completed_evaluations=self.session.scalar(
                select(func.count())
                .select_from(Evaluation)
                .where(Evaluation.status == EvaluationStatus.COMPLETED)
            )
            or 0,
            total_reports=count(Report),
            open_feedback=self.session.scalar(
                select(func.count())
                .select_from(Feedback)
                .where(Feedback.status != FeedbackStatus.RESOLVED)
            )
            or 0,
            ai_input_tokens=self.session.scalar(
                select(func.coalesce(func.sum(Evaluation.input_tokens), 0))
            )
            or 0,
            ai_output_tokens=self.session.scalar(
                select(func.coalesce(func.sum(Evaluation.output_tokens), 0))
            )
            or 0,
        )

    def users(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.created_at.desc()).limit(100)))

    def platform_insights(self) -> PlatformInsightsResponse:
        """Return bounded operational analytics for the administrator dashboard."""
        today = datetime.now(UTC).date()
        days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
        counts: dict[object, dict[str, int]] = defaultdict(lambda: {"users": 0, "projects": 0, "evaluations": 0})
        for user in self.session.scalars(select(User).where(User.created_at >= datetime.combine(days[0], datetime.min.time(), tzinfo=UTC))):
            counts[user.created_at.date()]["users"] += 1
        for project in self.session.scalars(select(Project).where(Project.created_at >= datetime.combine(days[0], datetime.min.time(), tzinfo=UTC))):
            counts[project.created_at.date()]["projects"] += 1
        for evaluation in self.session.scalars(select(Evaluation).where(Evaluation.created_at >= datetime.combine(days[0], datetime.min.time(), tzinfo=UTC))):
            counts[evaluation.created_at.date()]["evaluations"] += 1
        activity_trend = [TrendPoint(label=day.strftime("%d %b"), **counts[day]) for day in days]

        industry_rows = self.session.execute(
            select(StartupIdea.industry, func.count()).group_by(StartupIdea.industry).order_by(func.count().desc()).limit(6)
        ).all()
        industries = [DistributionItem(label=industry or "Unspecified", value=count) for industry, count in industry_rows]
        status_rows = self.session.execute(
            select(Evaluation.status, func.count()).group_by(Evaluation.status).order_by(func.count().desc())
        ).all()
        evaluation_statuses = [DistributionItem(label=str(status).replace("_", " ").title(), value=count) for status, count in status_rows]

        alerts: list[AdminAlertResponse] = []
        for user in self.session.scalars(select(User).order_by(User.created_at.desc()).limit(4)):
            alerts.append(AdminAlertResponse(id=f"user-{user.id}", title="New user account", detail=f"{user.full_name} registered as {user.role.value.replace('_', ' ')}.", severity="info", created_at=user.created_at))
        for item in self.session.scalars(select(Feedback).where(Feedback.status != FeedbackStatus.RESOLVED).order_by(Feedback.created_at.desc()).limit(4)):
            alerts.append(AdminAlertResponse(id=f"feedback-{item.id}", title="Feedback needs review", detail=f"{item.category}: {item.message[:100]}", severity="warning", created_at=item.created_at))
        for evaluation in self.session.scalars(select(Evaluation).where(Evaluation.status == EvaluationStatus.FAILED).order_by(Evaluation.created_at.desc()).limit(4)):
            alerts.append(AdminAlertResponse(id=f"evaluation-{evaluation.id}", title="AI evaluation failed", detail=evaluation.failure_reason or "A pipeline run needs investigation.", severity="error", created_at=evaluation.created_at))
        alerts.sort(key=lambda alert: alert.created_at, reverse=True)
        return PlatformInsightsResponse(activity_trend=activity_trend, industries=industries, evaluation_statuses=evaluation_statuses, alerts=alerts[:8])

    def update_user(
        self,
        user_id: str,
        *,
        is_active: bool | None = None,
        role: UserRole | None = None,
        is_email_verified: bool | None = None,
    ) -> User:
        user = self.session.get(User, user_id)
        if not user:
            raise ResourceNotFoundError("User was not found.")
        if is_active is not None:
            user.is_active = is_active
        if role is not None:
            user.role = role
        if is_email_verified is not None:
            user.is_email_verified = is_email_verified
        self.session.commit()
        self.session.refresh(user)
        return user

    def feedback(self) -> list[Feedback]:
        return list(
            self.session.scalars(select(Feedback).order_by(Feedback.created_at.desc()).limit(100))
        )

    def update_feedback(
        self, feedback_id: str, status: FeedbackStatus, note: str | None
    ) -> Feedback:
        feedback = self.session.get(Feedback, feedback_id)
        if not feedback:
            raise ResourceNotFoundError("Feedback was not found.")
        feedback.status = status
        feedback.admin_note = note
        self.session.commit()
        self.session.refresh(feedback)
        return feedback
