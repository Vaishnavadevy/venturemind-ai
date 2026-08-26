"""Provider-backed competitor discovery: Google Places first, OpenStreetMap fallback."""

from __future__ import annotations

import json
import time
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.competitor import CompetitorPlace, CompetitorSearchRequest, CompetitorSearchResponse


class CompetitorService:
    """Find public nearby listings without exposing external provider keys to browsers."""

    google_endpoint = "https://places.googleapis.com/v1/places:searchText"
    nominatim_endpoint = "https://nominatim.openstreetmap.org/search"
    overpass_endpoint = "https://overpass-api.de/api/interpreter"
    google_field_mask = ",".join(["places.id", "places.displayName", "places.formattedAddress", "places.primaryTypeDisplayName", "places.rating", "places.userRatingCount", "places.priceLevel", "places.websiteUri", "places.googleMapsUri"])
    _osm_cache: dict[str, tuple[float, list[CompetitorPlace]]] = {}
    _osm_lock = Lock()
    _last_nominatim_request = 0.0

    @staticmethod
    def _query(payload: CompetitorSearchRequest) -> str:
        location = ", ".join(item.strip() for item in [payload.city or "", payload.district or "", payload.country] if item.strip())
        return f"{payload.business_category.strip()} businesses in {location}"

    @staticmethod
    def _maps_url(query: str) -> str:
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"

    def search(self, payload: CompetitorSearchRequest) -> CompetitorSearchResponse:
        query = self._query(payload)
        maps_search_url = self._maps_url(query)
        if get_settings().google_places_api_key:
            return self._google_search(payload, query, maps_search_url)
        return self._openstreetmap_search(payload, query, maps_search_url)

    def _google_search(self, payload: CompetitorSearchRequest, query: str, maps_search_url: str) -> CompetitorSearchResponse:
        body = json.dumps({"textQuery": query, "pageSize": payload.max_results, "languageCode": "en"}).encode("utf-8")
        request = Request(self.google_endpoint, data=body, headers={"Content-Type": "application/json", "X-Goog-Api-Key": get_settings().google_places_api_key or "", "X-Goog-FieldMask": self.google_field_mask}, method="POST")
        try:
            with urlopen(request, timeout=10) as response:  # noqa: S310 - fixed Google endpoint
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code in {401, 403}:
                detail = "Google Places denied this request. Enable Places API (New), enable billing, and check the server API key restrictions."
            elif error.code == 429:
                detail = "Google Places quota has been reached. Check usage limits and try again later."
            else:
                detail = "Google Places rejected the competitor search request. Try again or check the Google Cloud configuration."
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail) from error
        except URLError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google Places is temporarily unavailable.") from error
        competitors = [CompetitorPlace(place_id=item.get("id", ""), name=item.get("displayName", {}).get("text", "Unnamed business"), address=item.get("formattedAddress"), primary_type=item.get("primaryTypeDisplayName", {}).get("text"), rating=item.get("rating"), user_rating_count=item.get("userRatingCount"), price_level=item.get("priceLevel"), website_url=item.get("websiteUri"), maps_url=item.get("googleMapsUri")) for item in data.get("places", [])]
        return CompetitorSearchResponse(provider_configured=True, provider="google_places", query=query, maps_search_url=maps_search_url, competitors=competitors, notice=None if competitors else "No matching Google Places listings were returned. Try a broader category or location.", attribution="Data from Google Maps Platform")

    def _openstreetmap_search(self, payload: CompetitorSearchRequest, query: str, maps_search_url: str) -> CompetitorSearchResponse:
        try:
            cache_key = "|".join([payload.business_category.lower(), payload.city or "", payload.district or "", payload.country, str(payload.max_results)])
            cached = self._osm_cache.get(cache_key)
            if cached and time.monotonic() - cached[0] < 300:
                competitors = cached[1]
            else:
                latitude, longitude = self._coordinates(payload)
                elements = self._overpass_elements(payload, latitude, longitude)
                competitors = self._osm_places(elements, payload.max_results)
                self._osm_cache[cache_key] = (time.monotonic(), competitors)
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
            return CompetitorSearchResponse(provider_configured=False, provider="none", query=query, maps_search_url=maps_search_url, notice="Live community-map listings are unavailable right now. Use the Google Maps link to search this location.")
        return CompetitorSearchResponse(provider_configured=True, provider="openstreetmap", query=query, maps_search_url=maps_search_url, competitors=competitors, notice="OpenStreetMap community data is being used because Google Places is not configured. Coverage, ratings, and website details may be incomplete. © OpenStreetMap contributors.", attribution="© OpenStreetMap contributors")

    def _coordinates(self, payload: CompetitorSearchRequest) -> tuple[float, float]:
        place = ", ".join(value for value in [payload.city, payload.district, payload.country] if value)
        with self._osm_lock:
            delay = 1 - (time.monotonic() - self._last_nominatim_request)
            if delay > 0:
                time.sleep(delay)
            self._last_nominatim_request = time.monotonic()
        request = Request(f"{self.nominatim_endpoint}?{urlencode({'q': place, 'format': 'jsonv2', 'limit': 1})}", headers={"User-Agent": get_settings().osm_user_agent, "Accept": "application/json"})
        with urlopen(request, timeout=10) as response:  # noqa: S310 - fixed Nominatim endpoint
            results = json.loads(response.read().decode("utf-8"))
        if not results:
            raise ValueError("Location was not found.")
        return float(results[0]["lat"]), float(results[0]["lon"])

    def _overpass_elements(self, payload: CompetitorSearchRequest, latitude: float, longitude: float) -> list[dict[str, object]]:
        tag_expression = self._osm_category_expression(payload.business_category)
        query = f"[out:json][timeout:20];(nwr{tag_expression}(around:5000,{latitude},{longitude}););out center tags;"
        request = Request(self.overpass_endpoint, data=urlencode({"data": query}).encode("utf-8"), headers={"User-Agent": get_settings().osm_user_agent, "Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        with urlopen(request, timeout=25) as response:  # noqa: S310 - fixed Overpass endpoint
            return json.loads(response.read().decode("utf-8")).get("elements", [])

    @staticmethod
    def _osm_category_expression(category: str) -> str:
        value = category.lower()
        if any(word in value for word in ("food", "cafe", "restaurant", "bakery", "beverage")):
            return '["amenity"~"cafe|restaurant|fast_food|food_court|ice_cream|bar|pub|bakery"]'
        if any(word in value for word in ("health", "medical", "pharmacy", "clinic")):
            return '["amenity"~"clinic|doctors|pharmacy|hospital"]'
        if any(word in value for word in ("retail", "shop", "store", "commerce")):
            return '["shop"]'
        return '["name"]["amenity"~"restaurant|cafe|fast_food|bank|pharmacy|clinic|school|marketplace"]'

    @staticmethod
    def _osm_places(elements: list[dict[str, object]], max_results: int) -> list[CompetitorPlace]:
        places: list[CompetitorPlace] = []
        for element in elements:
            tags = element.get("tags", {})
            if not isinstance(tags, dict) or not tags.get("name"):
                continue
            element_type, element_id = str(element.get("type", "node")), str(element.get("id", ""))
            address = ", ".join(str(tags[key]) for key in ("addr:housenumber", "addr:street", "addr:city") if tags.get(key)) or None
            primary_type = str(tags.get("amenity") or tags.get("shop") or "Business listing").replace("_", " ").title()
            places.append(CompetitorPlace(place_id=f"osm-{element_type}-{element_id}", name=str(tags["name"]), address=address, primary_type=primary_type, website_url=str(tags["website"]) if tags.get("website") else None, maps_url=f"https://www.openstreetmap.org/{element_type}/{element_id}"))
            if len(places) >= max_results:
                break
        return places
