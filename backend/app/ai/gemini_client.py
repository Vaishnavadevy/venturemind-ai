from google import genai

from app.core.config import get_settings
from app.core.exceptions import VentureMindError


class GeminiClient:
    def generate(self, prompt: str) -> str:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise VentureMindError("AI assistant is not configured.")
        response = genai.Client(api_key=settings.gemini_api_key).models.generate_content(
            model=settings.gemini_model, contents=prompt
        )
        if not response.text:
            raise VentureMindError("AI assistant returned an empty response.")
        return response.text
