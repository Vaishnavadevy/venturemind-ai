"""Domain exceptions kept independent from FastAPI."""


class VentureMindError(Exception):
    """Base exception for expected application errors."""

    status_code = 400
    code = "venturemind_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ResourceNotFoundError(VentureMindError):
    status_code = 404
    code = "resource_not_found"


class ConflictError(VentureMindError):
    status_code = 409
    code = "resource_conflict"
