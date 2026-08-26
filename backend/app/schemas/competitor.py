"""Contracts for location-aware competitor discovery."""

from pydantic import BaseModel, Field


class CompetitorSearchRequest(BaseModel):
    """A focused business and location query for Google Places Text Search."""

    business_category: str = Field(min_length=2, max_length=120)
    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    industry: str | None = Field(default=None, max_length=120)
    max_results: int = Field(default=5, ge=1, le=10)


class CompetitorPlace(BaseModel):
    """Public place information returned by the configured provider."""

    place_id: str
    name: str
    address: str | None = None
    primary_type: str | None = None
    rating: float | None = None
    user_rating_count: int | None = None
    price_level: str | None = None
    website_url: str | None = None
    maps_url: str | None = None


class CompetitorSearchResponse(BaseModel):
    """Search outcome, including a truthful fallback when provider access is absent."""

    provider_configured: bool
    provider: str = "none"
    query: str
    maps_search_url: str
    competitors: list[CompetitorPlace] = Field(default_factory=list)
    notice: str | None = None
    attribution: str | None = None
