from decimal import Decimal

from app.ai.confidence_engine import StartupConfidenceEngine
from app.models.enums import DevelopmentStage
from app.models.project import StartupIdea


def test_confidence_engine_is_deterministic_and_weighted() -> None:
    idea = StartupIdea(
        project_id="project-1",
        startup_name="CareLink",
        industry="HealthTech",
        country="Sri Lanka",
        target_audience="Urban adults who need faster, more reliable access to primary care services.",
        problem_statement="Patients spend too long finding trustworthy primary care and struggle to compare availability, price, and quality across providers.",
        proposed_solution="A personalized digital platform uses data and automation to match patients with available primary care providers.",
        business_model="A digital marketplace connects patients and providers through a self-service web and mobile platform.",
        revenue_model="Providers pay a subscription and a fee for completed bookings, with clear monthly pricing for clinics.",
        development_stage=DevelopmentStage.MVP,
        budget_amount=Decimal("5000"),
        budget_currency="USD",
        competitors=[{"name": "Example competitor"}],
        additional_notes="Initial interviews show the need for transparent appointment availability and pricing.",
    )
    engine = StartupConfidenceEngine()
    first = engine.evaluate(idea)
    second = engine.evaluate(idea)
    assert [(result.metric_key, result.score) for result in first] == [
        (result.metric_key, result.score) for result in second
    ]
    assert engine.overall_score(first) == sum(
        (result.score * result.weight for result in first), Decimal("0")
    ).quantize(Decimal("0.01"))
    assert {result.metric_key for result in first} == {
        "innovation",
        "market_opportunity",
        "business_model",
        "scalability",
        "technical_feasibility",
        "financial_feasibility",
        "risk_resilience",
        "investment_readiness",
    }
