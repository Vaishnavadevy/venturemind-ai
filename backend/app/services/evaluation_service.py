"""Orchestration of deterministic extraction, scoring, and explanations."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.business_analysis import BusinessAnalysisGenerator
from app.ai.confidence_engine import StartupConfidenceEngine
from app.ai.nlp_extractor import StartupNLPExtractor
from app.core.exceptions import ResourceNotFoundError
from app.models.enums import EvaluationStatus
from app.models.evaluation import Evaluation, EvaluationScore
from app.models.project import Project, StartupIdea
from app.models.user import User


class EvaluationService:
    pipeline_version = "deterministic-v1"

    def __init__(
        self,
        session: Session,
        extractor: StartupNLPExtractor | None = None,
        engine: StartupConfidenceEngine | None = None,
        analysis_generator: BusinessAnalysisGenerator | None = None,
    ) -> None:
        self.session = session
        self.extractor = extractor or StartupNLPExtractor()
        self.engine = engine or StartupConfidenceEngine()
        self.analysis_generator = analysis_generator or BusinessAnalysisGenerator()

    def evaluate_latest_idea(self, project_id: str, user: User) -> Evaluation:
        project = self.session.scalar(
            select(Project).where(Project.id == project_id, Project.owner_id == user.id)
        )
        if not project:
            raise ResourceNotFoundError("Project was not found.")
        idea = self.session.scalar(
            select(StartupIdea)
            .where(StartupIdea.project_id == project.id)
            .order_by(StartupIdea.version.desc())
        )
        if not idea:
            raise ResourceNotFoundError("Startup idea was not found.")
        return self.evaluate_idea(project, idea)

    def evaluate_idea(self, project: Project, idea: StartupIdea) -> Evaluation:
        extraction = self.extractor.extract(idea)
        results = self.engine.evaluate(idea)
        analysis = self.analysis_generator.generate(idea)
        evaluation = Evaluation(
            project_id=project.id,
            startup_idea_id=idea.id,
            status=EvaluationStatus.COMPLETED,
            pipeline_version=self.pipeline_version,
            overall_confidence_score=self.engine.overall_score(results),
            structured_extraction=extraction,
            recommendations=self._recommendations(results),
            risk_analysis=self._risk_analysis(results),
            completed_at=datetime.now(UTC),
            **analysis,
        )
        self.session.add(evaluation)
        self.session.flush()
        for result in results:
            self.session.add(
                EvaluationScore(
                    evaluation_id=evaluation.id,
                    metric_key=result.metric_key,
                    score=result.score,
                    weight=result.weight,
                    reasoning=result.reasoning,
                    positive_factors=result.positive_factors,
                    negative_factors=result.negative_factors,
                    improvement_suggestions=result.improvement_suggestions,
                    factor_breakdown=result.factor_breakdown,
                )
            )
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation

    @staticmethod
    def _recommendations(results: list) -> list[dict[str, str]]:
        weakest = sorted(results, key=lambda result: result.score)[:3]
        return [
            {
                "priority": "high" if index == 0 else "medium",
                "metric": result.metric_key,
                "recommendation": result.improvement_suggestions[0]
                if result.improvement_suggestions
                else "Maintain evidence and validate assumptions as the venture progresses.",
            }
            for index, result in enumerate(weakest)
        ]

    @staticmethod
    def _risk_analysis(results: list) -> dict[str, object]:
        score = next(result.score for result in results if result.metric_key == "risk_resilience")
        return {
            "risk_resilience_score": float(score),
            "level": "low" if score >= 75 else "moderate" if score >= 50 else "high",
            "note": "Risk level reflects the completeness of documented risk context, not a legal or financial risk opinion.",
        }
