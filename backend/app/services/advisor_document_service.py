"""Private encrypted storage for advisor-verification evidence.

Files are intentionally kept outside static/public directories and are only returned through
an authenticated administrator route. The encryption key must be supplied by environment.
"""

from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from cryptography.fernet import Fernet, InvalidToken
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ResourceNotFoundError, VentureMindError
from app.models.admin_management import AdvisorVerificationDocument, AdvisorVerificationRequest

MAX_DOCUMENT_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}


class AdvisorDocumentService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()

    def _fernet(self) -> Fernet:
        if not self.settings.advisor_document_encryption_key:
            raise VentureMindError("Advisor-document encryption is not configured. Set ADVISOR_DOCUMENT_ENCRYPTION_KEY on the server.")
        try:
            return Fernet(self.settings.advisor_document_encryption_key.encode())
        except ValueError as exc:
            raise VentureMindError("ADVISOR_DOCUMENT_ENCRYPTION_KEY is invalid. Generate a valid Fernet key before accepting documents.") from exc

    def _storage_dir(self) -> Path:
        directory = Path("private_uploads") / "advisor_documents"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    async def upload(self, request_id: str, upload: UploadFile) -> AdvisorVerificationDocument:
        request = self.session.get(AdvisorVerificationRequest, request_id)
        if not request:
            raise ResourceNotFoundError("Advisor verification request was not found.")
        if request.status != "pending":
            raise VentureMindError("Documents can only be added while verification is pending.")
        if upload.content_type not in ALLOWED_CONTENT_TYPES:
            raise VentureMindError("Only PDF, JPEG, and PNG verification documents are accepted.")
        raw = await upload.read(MAX_DOCUMENT_BYTES + 1)
        if not raw or len(raw) > MAX_DOCUMENT_BYTES:
            raise VentureMindError("Verification documents must be between 1 byte and 5 MB.")
        encrypted = self._fernet().encrypt(raw)
        storage_key = f"{uuid4().hex}.bin"
        (self._storage_dir() / storage_key).write_bytes(encrypted)
        retention_until = date.today() + timedelta(days=self.settings.advisor_document_retention_days)
        document = AdvisorVerificationDocument(
            verification_request_id=request.id,
            storage_key=storage_key,
            original_name=(upload.filename or "verification-document")[:255],
            content_type=upload.content_type,
            size_bytes=len(raw),
            checksum=sha256(raw).hexdigest(),
            retention_until=retention_until,
        )
        self.session.add(document)
        self.session.commit(); self.session.refresh(document)
        return document

    def list_for_request(self, request_id: str) -> list[AdvisorVerificationDocument]:
        return list(self.session.scalars(select(AdvisorVerificationDocument).where(AdvisorVerificationDocument.verification_request_id == request_id).order_by(AdvisorVerificationDocument.created_at.desc())))

    def read_for_admin(self, request_id: str, document_id: str) -> tuple[AdvisorVerificationDocument, bytes]:
        document = self.session.get(AdvisorVerificationDocument, document_id)
        if not document or document.verification_request_id != request_id:
            raise ResourceNotFoundError("Verification document was not found.")
        path = self._storage_dir() / document.storage_key
        if not path.exists():
            raise ResourceNotFoundError("The encrypted verification document is no longer available.")
        try:
            raw = self._fernet().decrypt(path.read_bytes())
        except InvalidToken as exc:
            raise VentureMindError("Verification document integrity check failed.") from exc
        if sha256(raw).hexdigest() != document.checksum:
            raise VentureMindError("Verification document checksum does not match.")
        return document, raw

    def purge_expired(self) -> int:
        """Retention task hook. Run later from a scheduled maintenance job."""
        documents = list(self.session.scalars(select(AdvisorVerificationDocument).where(AdvisorVerificationDocument.retention_until < date.today())))
        for document in documents:
            (self._storage_dir() / document.storage_key).unlink(missing_ok=True)
            self.session.delete(document)
        self.session.commit()
        return len(documents)
