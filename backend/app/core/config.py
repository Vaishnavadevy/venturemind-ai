"""Typed application configuration loaded from the environment."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve this once from the source file, rather than from the PowerShell
# working directory.  This ensures the API always loads backend/.env whether
# it is launched from the project root or the backend directory.
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration for the API service."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "VentureMind AI API"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "mysql+pymysql://venturemind:change-me@localhost:3306/venturemind"
    cors_origins: list[AnyHttpUrl] = []
    log_level: str = "INFO"
    jwt_secret_key: str = "replace-me-before-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    frontend_url: AnyHttpUrl = "http://localhost:5173"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    ollama_enabled: bool = True
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2:3b"
    google_places_api_key: str | None = None
    advisor_document_encryption_key: str | None = None
    advisor_document_retention_days: int = 365
    osm_user_agent: str = "VentureMindAI/0.1 (final-year academic project)"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """Permit a simple comma-delimited value as well as JSON lists."""
        if isinstance(value, str) and not value.lstrip().startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings instance for the current process."""
    return Settings()
