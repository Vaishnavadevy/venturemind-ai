"""Deterministic, documented startup-confidence scoring engine."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.models.project import StartupIdea


@dataclass(frozen=True)
class ScoreResult:
    metric_key: str
    score: Decimal
    weight: Decimal
    reasoning: str
    positive_factors: list[str]
    negative_factors: list[str]
    improvement_suggestions: list[str]
    factor_breakdown: dict[str, object]


class StartupConfidenceEngine:
    """Scores input completeness and evidence quality through repeatable rules.

    A score of 100 represents fully evidenced input against the published criteria;
    it is not a prediction of startup success. `risk_resilience` is high when
    identified risks are low or actively addressed.
    """

    weights = {
        "innovation": Decimal("0.12"),
        "market_opportunity": Decimal("0.17"),
        "business_model": Decimal("0.15"),
        "scalability": Decimal("0.11"),
        "technical_feasibility": Decimal("0.11"),
        "financial_feasibility": Decimal("0.12"),
        "risk_resilience": Decimal("0.10"),
        "investment_readiness": Decimal("0.12"),
    }

    def evaluate(self, idea: StartupIdea) -> list[ScoreResult]:
        """Return the explainable score cards that feed the overall score."""
        return [
            self._innovation(idea),
            self._market(idea),
            self._business_model(idea),
            self._scalability(idea),
            self._technical(idea),
            self._financial(idea),
            self._risk(idea),
            self._investment_readiness(idea),
        ]

    def overall_score(self, results: list[ScoreResult]) -> Decimal:
        total = sum((result.score * result.weight for result in results), Decimal("0"))
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _score(
        self,
        metric: str,
        points: int,
        possible: int,
        reasoning: str,
        positive: list[str],
        negative: list[str],
        suggestions: list[str],
        factors: dict[str, object],
    ) -> ScoreResult:
        score = Decimal(str(max(0, min(100, round(points / possible * 100)))))
        return ScoreResult(
            metric, score, self.weights[metric], reasoning, positive, negative, suggestions, factors
        )

    def _innovation(self, idea: StartupIdea) -> ScoreResult:
        text = idea.proposed_solution.lower()
        differentiators = [
            term
            for term in ("unique", "first", "automated", "personalized", "ai", "data", "platform")
            if term in text
        ]
        points = (
            30 + min(len(idea.proposed_solution) // 15, 35) + min(len(differentiators) * 12, 35)
        )
        positive = ["Solution is described in sufficient detail."]
        if differentiators:
            positive.append(f"Differentiation signals found: {', '.join(differentiators[:3])}.")
        negative = (
            [] if differentiators else ["No explicit differentiator is stated in the solution."]
        )
        return self._score(
            "innovation",
            points,
            100,
            "Scores solution specificity and explicitly stated differentiation.",
            positive,
            negative,
            ["State the unique advantage versus current alternatives."] if negative else [],
            {"solution_length": len(idea.proposed_solution), "differentiators": differentiators},
        )

    def _market(self, idea: StartupIdea) -> ScoreResult:
        audience = len(idea.target_audience)
        problem = len(idea.problem_statement)
        points = 20 + min(audience // 12, 40) + min(problem // 18, 40)
        positive = ["Target audience is defined."] if audience >= 20 else []
        negative = (
            []
            if problem >= 80
            else ["Problem evidence is brief; urgency and frequency are unclear."]
        )
        return self._score(
            "market_opportunity",
            points,
            100,
            "Scores clarity of the customer segment and problem evidence; it does not estimate external market size.",
            positive,
            negative,
            ["Add customer counts, market context, or interview evidence."] if negative else [],
            {"target_audience_characters": audience, "problem_statement_characters": problem},
        )

    def _business_model(self, idea: StartupIdea) -> ScoreResult:
        points = (
            25 + min(len(idea.business_model) // 12, 40) + min(len(idea.revenue_model) // 12, 35)
        )
        negative = (
            []
            if len(idea.revenue_model) >= 60
            else ["Revenue model lacks detail about pricing or payment mechanics."]
        )
        return self._score(
            "business_model",
            points,
            100,
            "Scores how clearly value delivery and revenue capture are described.",
            ["Business and revenue models are both supplied."],
            negative,
            ["Specify pricing, buyer, and payment frequency."] if negative else [],
            {
                "business_model_characters": len(idea.business_model),
                "revenue_model_characters": len(idea.revenue_model),
            },
        )

    def _scalability(self, idea: StartupIdea) -> ScoreResult:
        text = f"{idea.proposed_solution} {idea.business_model}".lower()
        signals = [
            term
            for term in (
                "software",
                "platform",
                "digital",
                "subscription",
                "automation",
                "marketplace",
                "network",
            )
            if term in text
        ]
        points = (
            35
            + min(len(signals) * 13, 52)
            + (
                13
                if idea.development_stage.value
                in {"mvp", "prototype", "testing", "launched", "growth"}
                else 0
            )
        )
        negative = (
            [] if signals else ["No repeatable or low-marginal-cost delivery signal is stated."]
        )
        return self._score(
            "scalability",
            points,
            100,
            "Scores stated repeatability, digital leverage, and execution maturity.",
            [f"Scalability signals: {', '.join(signals)}."] if signals else [],
            negative,
            ["Explain how delivery scales without proportional headcount growth."]
            if negative
            else [],
            {"scalability_signals": signals, "development_stage": idea.development_stage.value},
        )

    def _technical(self, idea: StartupIdea) -> ScoreResult:
        stage_points = {
            "idea": 30,
            "research": 38,
            "mvp": 62,
            "prototype": 55,
            "testing": 70,
            "launched": 78,
            "growth": 82,
        }[idea.development_stage.value]
        scope_points = min(len(idea.proposed_solution) // 10, 18)
        points = stage_points + scope_points
        negative = (
            []
            if idea.development_stage.value not in {"idea", "research"}
            else ["Technical feasibility is unvalidated at the current stage."]
        )
        return self._score(
            "technical_feasibility",
            points,
            100,
            "Scores current validation stage and solution implementation detail.",
            [f"Development stage is {idea.development_stage.value}."],
            negative,
            ["Define an MVP scope and test its highest-risk technical assumption."]
            if negative
            else [],
            {"development_stage_points": stage_points, "solution_detail_points": scope_points},
        )

    def _financial(self, idea: StartupIdea) -> ScoreResult:
        has_budget = idea.budget_amount is not None
        detailed_revenue = len(idea.revenue_model) >= 80
        points = (
            30
            + (30 if has_budget else 0)
            + (40 if detailed_revenue else min(len(idea.revenue_model) // 2, 30))
        )
        negative = ([] if has_budget else ["No initial budget is supplied."]) + (
            [] if detailed_revenue else ["Revenue assumptions need more detail."]
        )
        return self._score(
            "financial_feasibility",
            points,
            100,
            "Scores the presence of budget and revenue assumptions, not projected profitability.",
            (["Initial budget is supplied."] if has_budget else [])
            + (["Revenue model includes useful detail."] if detailed_revenue else []),
            negative,
            ["Add startup costs, monthly operating costs, price, and expected customer volume."]
            if negative
            else [],
            {"budget_provided": has_budget, "revenue_model_characters": len(idea.revenue_model)},
        )

    def _risk(self, idea: StartupIdea) -> ScoreResult:
        competitor_count = len(idea.competitors)
        notes = len(idea.additional_notes or "")
        points = 45 + min(competitor_count * 10, 30) + min(notes // 20, 25)
        negative = (
            []
            if competitor_count
            else ["No competitors are identified, so competitive risk has not been assessed."]
        )
        return self._score(
            "risk_resilience",
            points,
            100,
            "Scores whether known risks and competitive context have been considered.",
            ([f"{competitor_count} competitor(s) supplied."] if competitor_count else [])
            + (["Additional constraints or assumptions are documented."] if notes >= 80 else []),
            negative,
            [
                "Identify direct and indirect alternatives, plus your key legal, market, and operational risks."
            ]
            if negative
            else [],
            {"competitor_count": competitor_count, "additional_notes_characters": notes},
        )

    def _investment_readiness(self, idea: StartupIdea) -> ScoreResult:
        stage = idea.development_stage.value
        mature = stage in {"mvp", "prototype", "testing", "launched", "growth"}
        points = (
            20
            + (25 if mature else 0)
            + min(len(idea.problem_statement) // 20, 25)
            + min(len(idea.business_model) // 20, 20)
            + (10 if idea.budget_amount is not None else 0)
        )
        negative = (
            []
            if mature
            else ["The concept is pre-validation, which limits current investor readiness."]
        )
        return self._score(
            "investment_readiness",
            points,
            100,
            "Scores evidence readiness for an investor conversation, not funding eligibility.",
            (["Idea has progressed beyond initial research."] if mature else [])
            + (["Budget assumption is included."] if idea.budget_amount is not None else []),
            negative,
            ["Validate demand, document traction, and prepare basic unit economics."]
            if negative
            else [],
            {"development_stage": stage, "budget_provided": idea.budget_amount is not None},
        )
