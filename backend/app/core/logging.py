"""Structured, process-wide logging setup."""

import logging


def configure_logging(level: str) -> None:
    """Configure logging once at application startup."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
