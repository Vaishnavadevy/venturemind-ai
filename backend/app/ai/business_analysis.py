"""Transparent, deterministic business planning artifacts."""

from app.models.project import StartupIdea


class BusinessAnalysisGenerator:
    def generate(self, idea: StartupIdea) -> dict[str, object]:
        competitors = (
            ", ".join(item.get("name", "an alternative") for item in idea.competitors[:3])
            or "known alternatives"
        )
        return {
            "swot_analysis": {
                "strengths": ["Clearly stated customer problem.", "Defined target audience."],
                "weaknesses": ["Submitted assumptions require customer validation."],
                "opportunities": [f"Test demand within {idea.industry} in {idea.country}."],
                "threats": [f"Customers may continue using {competitors}."],
            },
            "business_model_canvas": {
                "value_proposition": idea.proposed_solution,
                "customer_segments": idea.target_audience,
                "channels": "Validate acquisition channels through experiments.",
                "customer_relationships": "Start with high-touch onboarding, then standardize support.",
                "revenue_streams": idea.revenue_model,
                "key_resources": "Customer insight, product capability, and domain knowledge.",
                "key_activities": "Customer discovery, MVP delivery, measurement, and iteration.",
                "key_partners": "Distribution partners, domain experts, and technology providers.",
                "cost_structure": "Product development, acquisition experiments, operations, and compliance.",
            },
            "market_analysis": {
                "market_demand": "Validate demand with target customers; the submitted problem indicates a potential unmet need.",
                "market_size": "No market-size estimate is stated without sourced external data.",
                "industry_trends": f"Investigate {idea.industry} trends and regulations relevant to {idea.country}.",
                "growth_potential": "Growth depends on repeatable acquisition, retention, and sustainable unit economics.",
            },
            "roadmap": [
                {
                    "phase": "Research",
                    "milestone": "Interview target customers.",
                    "outcome": "Validated problem evidence",
                },
                {
                    "phase": "MVP",
                    "milestone": "Build the smallest testable solution.",
                    "outcome": "Demand signal",
                },
                {
                    "phase": "Testing",
                    "milestone": "Measure activation and willingness to pay.",
                    "outcome": "Evidence-led iteration",
                },
                {
                    "phase": "Launch",
                    "milestone": "Define repeatable go-to-market.",
                    "outcome": "Early traction",
                },
                {
                    "phase": "Growth",
                    "milestone": "Improve unit economics and delivery.",
                    "outcome": "Sustainable plan",
                },
            ],
        }
