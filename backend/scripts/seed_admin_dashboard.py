"""Create safe, repeatable local demo data for the VentureMind admin dashboard.

This script only adds records with the `demo-` project-name prefix and the
`@venturemind.demo` email domain. It never deletes or edits existing user data.
Run it only in a local/development database.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import (
    DevelopmentStage,
    EvaluationStatus,
    FeedbackStatus,
    NotificationType,
    ProjectStatus,
    ReportStatus,
    UserRole,
)
from app.models.evaluation import Evaluation, EvaluationScore
from app.models.feedback import Feedback
from app.models.lifecycle import LifecycleMilestone, StartupProfile
from app.models.notification import Notification
from app.models.platform_announcement import PlatformAnnouncement
from app.models.project import Project, StartupIdea
from app.models.report import Report
from app.models.user import User
from app.schemas.financial_plan import FinancialPlanInput
from app.schemas.lifecycle import StartupProfileUpsert
from app.services.business_registration_service import BusinessRegistrationService
from app.services.financial_plan_service import FinancialPlanService
from app.services.lifecycle_service import LifecycleService


DEMO_PASSWORD = "VentureMindDemo@2026"


def first_or_create(session, model, *, filters: dict[str, object], **values):
    item = session.scalar(select(model).filter_by(**filters))
    if item is None:
        item = model(**values)
        session.add(item)
        session.flush()
    return item


def create_project_bundle(session, founder: User, offset: int, name: str, industry: str, score: int) -> None:
    project = first_or_create(
        session,
        Project,
        filters={"owner_id": founder.id, "name": f"demo-{name}"},
        owner_id=founder.id,
        name=f"demo-{name}",
        description=f"Demonstration startup project for {name}.",
        status=ProjectStatus.ACTIVE,
        created_at=datetime.now(UTC) - timedelta(days=offset),
    )


    idea = first_or_create(
        session,
        StartupIdea,
        filters={"project_id": project.id, "version": 1},
        project_id=project.id,
        version=1,
        startup_name=name,
        industry=industry,
        country="Sri Lanka",
        target_audience="Local small-business owners and early customers",
        problem_statement="Customers need a clearer, more reliable way to solve a recurring local problem.",
        proposed_solution="A focused digital and service-based solution validated through customer interviews.",
        business_model="Direct service and subscription model",
        revenue_model="Monthly subscription and transaction revenue",
        development_stage=DevelopmentStage.MVP,
        budget_amount=Decimal("750000.00"),
        budget_currency="LKR",
        competitors=[],
        additional_notes="Local demo data for the administrator dashboard.",
        created_at=datetime.now(UTC) - timedelta(days=offset),
    )
    evaluation = first_or_create(
        session,
        Evaluation,
        filters={"project_id": project.id, "startup_idea_id": idea.id, "pipeline_version": "dashboard-demo-v1"},
        project_id=project.id,
        startup_idea_id=idea.id,
        status=EvaluationStatus.COMPLETED,
        pipeline_version="dashboard-demo-v1",
        overall_confidence_score=Decimal(str(score)),
        structured_extraction={"industry": industry, "country": "Sri Lanka"},
        risk_analysis={"summary": "Demonstration evaluation for dashboard charts."},
        recommendations=[{"title": "Validate demand", "detail": "Interview target customers before increasing spend."}],
        llm_model="structured-local-guidance",
        input_tokens=520 + offset * 35,
        output_tokens=190 + offset * 20,
        completed_at=datetime.now(UTC) - timedelta(days=offset),
        created_at=datetime.now(UTC) - timedelta(days=offset),
    )
    demo_suggestions = {
        "market_opportunity": "Interview 10 target customers in your launch area and record the problem they already pay to solve.",
        "business_model": "Test one simple price point with prospective customers before committing to a full launch budget.",
        "scalability": "Document the repeatable delivery process and identify the first capacity constraint before expanding.",
    }
    for metric, metric_score in [("market_opportunity", score + 4), ("business_model", score - 2), ("scalability", score + 1)]:
        evaluation_score = first_or_create(
            session,
            EvaluationScore,
            filters={"evaluation_id": evaluation.id, "metric_key": metric},
            evaluation_id=evaluation.id,
            metric_key=metric,
            score=Decimal(str(max(0, min(100, metric_score)))),
            weight=Decimal("0.3333"),
            reasoning="Demo evidence-based factor used to populate the administration dashboard.",
            positive_factors=["Business profile includes a target customer and revenue approach."],
            negative_factors=["Additional customer validation is required."],
            improvement_suggestions=[demo_suggestions[metric]],
        )
        # These are demo-only records, so improving their labels on later runs is safe.
        evaluation_score.improvement_suggestions = [demo_suggestions[metric]]
    first_or_create(
        session,
        Report,
        filters={"project_id": project.id, "file_name": f"{name.lower().replace(' ', '-')}-startup-report.pdf"},
        project_id=project.id,
        evaluation_id=evaluation.id,
        status=ReportStatus.READY,
        storage_key=f"demo-reports/{project.id}.pdf",
        file_name=f"{name.lower().replace(' ', '-')}-startup-report.pdf",
        mime_type="application/pdf",
        file_size_bytes=184_000,
        generated_at=datetime.now(UTC) - timedelta(days=offset),
        created_at=datetime.now(UTC) - timedelta(days=offset),
    )


def create_lifecycle_demo(session, founder: User, name: str, category: str, offset: int) -> None:
    """Add the workspace records used by the modern founder dashboard.

    The classic project/evaluation bundle is retained for evaluation-history and
    report demonstrations. This companion record makes the guided journey,
    smart recommendations, finance and registration cards coherent too.
    """
    profile = session.scalar(select(StartupProfile).where(StartupProfile.created_by_id == founder.id))
    lifecycle = LifecycleService(session)
    if profile is None:
        profile = lifecycle.create_profile(founder, StartupProfileUpsert(
            business_name=name, category=category, industry=category,
            description=f"{name} is a locally focused {category.lower()} startup serving customers in Jaffna.",
            target_customers="Students, families, office workers, and nearby residents",
            country="Sri Lanka", district="Jaffna", city="Jaffna",
            expected_investment=Decimal("750000.00"), available_budget=Decimal("500000.00"),
            business_experience="Early-stage founder with local market knowledge.",
            business_goals="Validate demand, launch a focused MVP, and grow sustainably.",
            business_size="Micro business", startup_type="New venture", partner_count=2,
            expected_employees=3, launch_timeline="Within 6 months",
        ))

    if not session.scalar(select(LifecycleMilestone.id).where(
        LifecycleMilestone.startup_profile_id == profile.id,
        LifecycleMilestone.milestone_key == "idea_created",
        LifecycleMilestone.completed_at.is_not(None),
    )):
        lifecycle.set_milestone(founder, profile.id, "idea_created", True)
    if offset <= 6:
        lifecycle.assess_risk(founder, profile.id)

    plan_marker = session.scalar(select(LifecycleMilestone.id).where(
        LifecycleMilestone.startup_profile_id == profile.id,
        LifecycleMilestone.milestone_key == "financial_plan_created",
    ))
    if offset <= 4 and not plan_marker:
        FinancialPlanService(session).create(founder, profile.id, FinancialPlanInput(
            partner_count=2, monthly_rent=65000, monthly_salary_cost=120000,
            monthly_marketing_cost=30000, monthly_other_cost=25000,
            expected_monthly_revenue=420000, gross_margin_percent=55,
        ))
        session.add(LifecycleMilestone(
            startup_profile_id=profile.id, milestone_key="financial_plan_created",
            title="Financial Plan Created", completed_at=datetime.now(UTC) - timedelta(days=max(offset - 1, 0)),
        ))
        session.commit()
    if offset <= 2:
        lifecycle.set_milestone(founder, profile.id, "requirements_completed", True)

    # The guide is demonstration-only and never submits data to a government service.
    try:
        registration = BusinessRegistrationService(session).start(founder, "demo")
        if offset <= 4:
            for item in registration.items[:2]:
                BusinessRegistrationService(session).update_item(founder, item.id, "completed")
    except Exception as exc:
        session.rollback()
        print(f"Registration demo data skipped for {founder.email}: {exc}")


def main() -> None:
    session = SessionLocal()
    try:
        admin = first_or_create(
            session,
            User,
            filters={"email": "admin@venturemind.demo"},
            email="admin@venturemind.demo",
            password_hash=hash_password(DEMO_PASSWORD),
            full_name="VentureMind Demo Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        founders = []
        for index, (name, email) in enumerate([
            ("Amara Silva", "amara@venturemind.demo"),
            ("Kavin Raj", "kavin@venturemind.demo"),
            ("Nethmi Perera", "nethmi@venturemind.demo"),
            ("Sahan Fernando", "sahan@venturemind.demo"),
        ]):
            founder = first_or_create(
                session,
                User,
                filters={"email": email},
                email=email,
                password_hash=hash_password(DEMO_PASSWORD),
                full_name=name,
                role=UserRole.FOUNDER,
                is_active=True,
                is_email_verified=True,
                created_at=datetime.now(UTC) - timedelta(days=6 - index),
            )
            founders.append(founder)

        for founder, payload in zip(founders, [
            (6, "Jaffna FoodLink", "Food & Beverage", 68),
            (4, "Lanka LearnHub", "Education Technology", 76),
            (2, "CareRoute", "Health Technology", 72),
            (1, "GreenCart Local", "Retail", 64),
        ], strict=True):
            create_project_bundle(session, founder, *payload)
            create_lifecycle_demo(session, founder, payload[1], payload[2], payload[0])

        for founder, category, message, rating, status in [
            (founders[0], "Competitor analysis", "Please add more local industry benchmark guidance for Jaffna founders.", 4, FeedbackStatus.OPEN),
            (founders[1], "Reports", "The PDF planning summary is useful; a share link would help team discussions.", 5, FeedbackStatus.IN_REVIEW),
            (founders[2], "Advisor bookings", "The appointment status was clear and easy to follow.", 5, FeedbackStatus.RESOLVED),
        ]:
            first_or_create(
                session,
                Feedback,
                filters={"user_id": founder.id, "category": category},
                user_id=founder.id,
                category=category,
                message=message,
                rating=rating,
                status=status,
                admin_note="Demo record for administrator dashboard review." if status != FeedbackStatus.OPEN else None,
            )

        for founder in founders[:2]:
            first_or_create(
                session,
                Notification,
                filters={"user_id": founder.id, "title": "Your startup evaluation is ready"},
                user_id=founder.id,
                notification_type=NotificationType.EVALUATION_READY,
                title="Your startup evaluation is ready",
                body="Open your dashboard to review explainable scores and recommended next actions.",
                payload={"path": "/dashboard"},
                is_read=False,
            )

        first_or_create(
            session,
            PlatformAnnouncement,
            filters={"title": "Welcome to the VentureMind demonstration workspace"},
            title="Welcome to the VentureMind demonstration workspace",
            message="Sample data is available to demonstrate analytics, reports, feedback and project workflows.",
            audience="all",
            is_active=True,
            created_by_id=admin.id,
        )
        session.commit()
        print("Demo dashboard data created successfully.")
        print("Admin login: admin@venturemind.demo")
        print(f"Temporary password: {DEMO_PASSWORD}")
        print("Change the temporary password or remove demo accounts before any public deployment.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
