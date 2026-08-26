"""Shared HTTP response contracts."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Consistent envelope for successful API responses."""

    model_config = ConfigDict(populate_by_name=True)

    data: T
    message: str | None = None


class ErrorDetail(BaseModel):
    """Machine-readable description of a failed request."""

    code: str
    message: str
    fields: dict[str, list[str]] | None = None


class ErrorResponse(BaseModel):
    """Consistent envelope for errors returned by the API."""

    error: ErrorDetail


class HealthStatus(BaseModel):
    """Service health payload."""

    status: str = Field(default="ok", examples=["ok"])
    environment: str
