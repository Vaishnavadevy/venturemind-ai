"""Editable AI suggestions for an unfinished founder profile."""

import json
import logging
from typing import Any

from app.ai.gemini_client import GeminiClient
from app.schemas.lifecycle import ProfileSuggestionRequest, ProfileSuggestions

logger = logging.getLogger(__name__)


class ProfileSuggestionService:
    """Produces short drafts; it never saves or treats suggestions as facts."""

    def suggest(self, request: ProfileSuggestionRequest) -> tuple[ProfileSuggestions, str, str]:
        fallback = self._fallback(request)
        prompt = (
            "You generate editable startup-profile drafts. Use only the supplied business name, category and location. "
            "Do not claim facts about competitors, prices, laws, demand, licenses, or success. Return valid JSON only "
            "with exactly these string keys: industry, startup_type, target_customers, description, next_question. "
            "Keep each value concise and write assumptions as suggestions.\n"
            f"Input: {request.model_dump()}"
        )
        try:
            generated = self._parse(GeminiClient().generate(prompt), fallback)
            return generated, "gemini", "Gemini produced editable draft suggestions. Review every field before saving."
        except Exception as exc:
            logger.info("Profile suggestion fallback used: %s", exc)
            return fallback, "structured_fallback", "Structured category-based suggestions are shown because live Gemini is unavailable. Review every field before saving."

    @staticmethod
    def _parse(text: str, fallback: ProfileSuggestions) -> ProfileSuggestions:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        value: Any = json.loads(cleaned)
        if not isinstance(value, dict):
            raise ValueError("Gemini response was not a JSON object.")
        allowed = {key: str(value.get(key, "")).strip()[:1000] for key in ProfileSuggestions.model_fields}
        merged = {key: allowed[key] or getattr(fallback, key) for key in ProfileSuggestions.model_fields}
        return ProfileSuggestions(**merged)

    @staticmethod
    def _fallback(request: ProfileSuggestionRequest) -> ProfileSuggestions:
        category = request.category.lower()
        name = request.business_name.strip()
        location = request.city or request.country or "the intended local market"
        if any(word in category for word in ("food", "cafe", "restaurant", "bakery", "beverage")):
            return ProfileSuggestions(industry="Food and beverage", startup_type="New venture", target_customers="Nearby residents, students, office workers, and families seeking convenient food or drinks.", description=f"{name} is a proposed food and beverage business serving customers in {location}.", next_question="What specific food or drink offer, price range, and customer problem will make this business different?")
        if any(word in category for word in ("retail", "shop", "commerce", "store")):
            return ProfileSuggestions(industry="Retail and commerce", startup_type="New venture", target_customers="Customers in the local market who need a convenient, reliable way to buy the selected products.", description=f"{name} is a proposed retail business serving customers in {location}.", next_question="Which products will you sell first, and why will customers choose you instead of existing sellers?")
        if any(word in category for word in ("software", "app", "technology", "ai", "saas")):
            return ProfileSuggestions(industry="Technology and software", startup_type="New venture", target_customers="A clearly defined customer group with a repeated workflow or problem that the product can improve.", description=f"{name} is a proposed technology venture designed to solve a specific customer problem.", next_question="Which customer workflow will the first MVP improve, and how will you measure whether users value it?")
        return ProfileSuggestions(industry=request.category.title(), startup_type="New venture", target_customers="A clearly defined group of customers who experience the problem this business intends to solve.", description=f"{name} is a proposed {request.category.lower()} business for customers in {location}.", next_question="What customer problem will you solve first, and how will you test willingness to pay?")
