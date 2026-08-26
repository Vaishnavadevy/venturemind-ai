# Architecture Notes

VentureMind AI separates delivery concerns from core business logic. API endpoints remain thin; services coordinate use cases; repositories isolate persistence; and AI adapters isolate external model providers. This makes evaluation logic testable without HTTP, databases, or an LLM.

The scoring engine will be deterministic and factor-based. LLM output will enrich narrative analysis but will not be the source of numeric confidence scores.
