"""Deterministic extraction of useful startup-idea context.

This rule-based baseline is deliberately dependency-free. Provider-backed NLP adapters
can be added later without changing the evaluation service contract.
"""

import re

from app.models.project import StartupIdea


class StartupNLPExtractor:
    """Build a structured snapshot from the submitted startup idea."""

    def extract(self, idea: StartupIdea) -> dict[str, object]:
        combined_text = " ".join(
            [
                idea.target_audience,
                idea.problem_statement,
                idea.proposed_solution,
                idea.business_model,
                idea.revenue_model,
                idea.additional_notes or "",
            ]
        )
        words = re.findall(r"[A-Za-z][A-Za-z-]{2,}", combined_text.lower())
        ignored = {
            "that",
            "with",
            "this",
            "from",
            "will",
            "your",
            "their",
            "they",
            "have",
            "into",
            "through",
            "business",
            "customers",
        }
        frequencies: dict[str, int] = {}
        for word in words:
            if word not in ignored:
                frequencies[word] = frequencies.get(word, 0) + 1
        keywords = [
            word
            for word, _ in sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))[:10]
        ]
        pain_points = [
            sentence.strip()
            for sentence in re.split(r"[.!?]", idea.problem_statement)
            if sentence.strip()
        ][:3]
        return {
            "industry": idea.industry,
            "keywords": keywords,
            "target_audience": idea.target_audience,
            "revenue_model": idea.revenue_model,
            "customer_pain_points": pain_points,
            "proposed_solution": idea.proposed_solution,
            "business_model": idea.business_model,
        }
