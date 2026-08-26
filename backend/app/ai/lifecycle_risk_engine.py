"""Deterministic, explainable risk scoring for saved lifecycle profiles."""

from dataclasses import dataclass
from decimal import Decimal

from app.models.lifecycle import StartupProfile


@dataclass(frozen=True)
class RiskScore:
    key: str
    label: str
    risk_score: int
    reasoning: str
    positive_factors: list[str]
    negative_factors: list[str]
    suggestions: list[str]


class LifecycleRiskEngine:
    """Scores documented evidence and planning readiness; never predicts success."""

    weights = {"market": 0.18, "financial": 0.18, "competition": 0.14, "customer": 0.14, "operational": 0.12, "legal": 0.10, "scalability": 0.14}

    @staticmethod
    def _card(key: str, label: str, base: int, checks: list[tuple[bool, int, str]], suggestion: str) -> RiskScore:
        positives = [message for passed, _, message in checks if passed]
        negatives = [message for passed, _, message in checks if not passed]
        score = max(5, min(95, base - sum(points for passed, points, _ in checks if passed)))
        return RiskScore(key, label, score, f"Risk falls when the profile contains evidence relevant to {label.lower()}.", positives, negatives, [suggestion] if negatives else ["Keep this evidence current as the business develops."])

    def evaluate(self, profile: StartupProfile) -> list[RiskScore]:
        # Numeric columns are returned by SQLAlchemy/MySQL as Decimal values.
        # Keep the threshold Decimal too; mixing Decimal with a float raises a
        # TypeError and prevents the evidence-based assessment from being saved.
        budget_coverage = bool(
            profile.expected_investment
            and profile.available_budget
            and profile.available_budget >= profile.expected_investment * Decimal("0.50")
        )
        location = bool(profile.city or profile.district)
        content = " ".join(filter(None, [profile.description, profile.target_customers, profile.business_goals, profile.industry, profile.startup_type])).lower()
        digital = any(term in content for term in ("digital", "platform", "software", "online", "subscription", "automation"))
        demand_evidence = any(term in content for term in ("interview", "survey", "demand", "pre-order", "customer feedback", "willingness to pay"))
        differentiation = any(term in content for term in ("unique", "faster", "affordable", "convenient", "specialised", "different", "gap"))
        operations_evidence = any(term in content for term in ("supplier", "delivery", "inventory", "process", "equipment", "workflow"))
        regulated_business = any(term in content for term in ("food", "health", "medical", "finance", "transport", "tourism", "import", "education"))
        customer_detail = len(profile.target_customers or "") >= 80
        return [
            self._card("market_risk", "Market risk", 82, [(len(profile.description) >= 160, 18, "The business offer is described in detail."), (location, 12, "A target location is specified."), (bool(profile.industry), 8, "An industry is specified."), (demand_evidence, 14, "Customer-demand evidence is recorded.")], "Interview target customers and document local demand before committing capital."),
            self._card("financial_risk", "Financial risk", 88, [(bool(profile.expected_investment), 20, "Expected investment is recorded."), (bool(profile.available_budget), 20, "Available budget is recorded."), (budget_coverage, 20, "Available budget covers at least half of expected investment.")], "Build a monthly cash-flow, operating-cost, and break-even plan."),
            self._card("competition_risk", "Competition risk", 78, [(location, 18, "A competitor-search location is available."), (len(profile.description) >= 120, 12, "The offer is detailed enough to compare against alternatives."), (bool(profile.category), 12, "A business category is specified."), (differentiation, 12, "A differentiation claim is documented.")], "Use the competitor search, compare pricing and differentiation, then define your market gap."),
            self._card("customer_risk", "Customer risk", 84, [(customer_detail, 24, "Target customers are described in detail."), (len(profile.business_goals or "") >= 60, 12, "Business goals are documented."), (demand_evidence, 16, "Customer-validation evidence is recorded.")], "Run customer interviews and test willingness to pay with a small target segment."),
            self._card("operational_risk", "Operational risk", 80, [(bool(profile.business_experience), 18, "Founder experience is documented."), (profile.expected_employees > 0, 12, "Expected staffing is planned."), (bool(profile.launch_timeline), 14, "A launch timeline is defined."), (operations_evidence, 12, "Operational delivery evidence is recorded.")], "List suppliers, daily operating processes, roles, and contingency actions."),
            self._card("legal_risk", "Legal risk", 86, [(bool(profile.country), 16, "Country is recorded for legal guidance."), (location, 10, "Local authority area is recorded."), (regulated_business, 8, "The profile identifies a regulated-sector requirement.")], "Verify registration, tax, licence, sector, and local-authority requirements before launch."),
            self._card("scalability_risk", "Scalability risk", 79, [(digital, 25, "Digital or repeatable delivery signals are present."), (profile.partner_count > 1, 8, "More than one partner is planned."), (profile.expected_employees > 0, 8, "A team plan is recorded.")], "Define repeatable processes and growth capacity that do not depend only on founder time."),
        ]

    def summary(self, scores: list[RiskScore]) -> tuple[float, float, float, str]:
        overall_risk = round(sum(score.risk_score * self.weights[score.key.removesuffix("_risk")] for score in scores), 2)
        confidence = round(100 - overall_risk, 2)
        success = round(confidence * 0.7 + (100 - max(score.risk_score for score in scores)) * 0.3, 2)
        level = "high" if overall_risk >= 70 else "moderate" if overall_risk >= 40 else "low"
        return success, confidence, overall_risk, level
