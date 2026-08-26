"""Turns deterministic risk evidence into readable local-AI guidance."""

import logging

from app.ai.lifecycle_risk_engine import RiskScore
from app.ai.ollama_client import OllamaClient
from app.models.lifecycle import StartupProfile

logger = logging.getLogger(__name__)


class ExplainableAIService:
    def explain(self, profile: StartupProfile, scores: list[RiskScore]) -> dict[str, object]:
        evidence = [{"area": score.label, "risk_score": score.risk_score, "positive_factors": score.positive_factors, "missing_evidence": score.negative_factors, "next_action": score.suggestions[0]} for score in scores]
        prompt = (
            "You are VentureMind's Explainable AI assistant. Do not calculate, change, or predict scores. "
            "Explain only the supplied deterministic evidence. Return valid JSON only with keys: summary, strongest_evidence, "
            "priority_gap, next_actions (array of 3 short actions), assumptions (array). Keep claims cautious.\n"
            f"Startup: {profile.business_name}; category: {profile.category}; location: {profile.city or profile.district or profile.country or 'not specified'}; "
            f"offer: {profile.description}; customers: {profile.target_customers or 'not specified'}; deterministic evidence: {evidence}"
        )
        try:
            result = OllamaClient().generate_json(prompt)
            return {"mode": "ollama", "model": "local", "summary": str(result.get("summary", "")), "strongest_evidence": str(result.get("strongest_evidence", "")), "priority_gap": str(result.get("priority_gap", "")), "next_actions": [str(value) for value in result.get("next_actions", [])][:3], "assumptions": [str(value) for value in result.get("assumptions", [])][:3]}
        except Exception as exc:  # Local AI is optional; deterministic fallback remains reliable.
            logger.info("Local Ollama explanation unavailable: %s", exc)
            weakest = sorted(scores, key=lambda score: score.risk_score, reverse=True)[:3]
            strongest = min(scores, key=lambda score: score.risk_score)
            return {"mode": "structured_fallback", "model": None, "summary": f"The scorecard is based on your saved startup profile. {weakest[0].label} needs the most attention before further investment.", "strongest_evidence": strongest.positive_factors[0] if strongest.positive_factors else "No strong evidence has been recorded yet.", "priority_gap": weakest[0].negative_factors[0] if weakest[0].negative_factors else weakest[0].suggestions[0], "next_actions": [score.suggestions[0] for score in weakest], "assumptions": ["Scores are decision support, not a prediction of business success."]}
