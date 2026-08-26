"""Startup-project submission use case."""

from sqlalchemy.orm import Session

from app.models.enums import ProjectStatus
from app.models.project import Project, StartupIdea
from app.models.user import User
from app.schemas.project import CreateProjectRequest


class ProjectService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_project(
        self, owner: User, payload: CreateProjectRequest
    ) -> tuple[Project, StartupIdea]:
        """Create a project and its immutable first startup-idea version atomically."""
        project = Project(owner_id=owner.id, name=payload.startup_name, status=ProjectStatus.ACTIVE)
        idea = StartupIdea(
            project=project,
            version=1,
            startup_name=payload.startup_name,
            industry=payload.industry,
            country=payload.country,
            target_audience=payload.target_audience,
            problem_statement=payload.problem_statement,
            proposed_solution=payload.proposed_solution,
            business_model=payload.business_model,
            revenue_model=payload.revenue_model,
            development_stage=payload.development_stage,
            budget_amount=payload.budget_amount,
            budget_currency=payload.budget_currency.upper() if payload.budget_currency else None,
            competitors=[{"name": competitor} for competitor in payload.competitors],
            additional_notes=payload.additional_notes,
        )
        self.session.add(project)
        self.session.add(idea)
        self.session.commit()
        self.session.refresh(project)
        self.session.refresh(idea)
        return project, idea
