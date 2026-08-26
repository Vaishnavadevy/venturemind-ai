"""Email delivery abstraction; production adapters can replace the logging adapter."""

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class EmailSender(Protocol):
    def send(self, recipient: str, subject: str, body: str) -> None: ...


class LoggingEmailSender:
    """Development-safe sender that never transmits credentials or user data externally."""

    def send(self, recipient: str, subject: str, body: str) -> None:
        logger.info("Email queued for recipient=%s subject=%s body=%s", recipient, subject, body)
