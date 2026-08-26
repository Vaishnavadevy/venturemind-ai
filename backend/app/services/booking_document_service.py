"""Private encrypted storage for founder documents shared with an advisor."""

from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from cryptography.fernet import Fernet
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.advisor import AdvisorSharedDocument


class BookingDocumentService:
    """Stores encrypted bytes outside the web root; callers enforce booking access."""

    allowed_types = {"application/pdf", "image/png", "image/jpeg"}
    max_bytes = 5 * 1024 * 1024

    def __init__(self, session: Session) -> None:
        self.session = session
        key = get_settings().advisor_document_encryption_key
        if not key:
            raise HTTPException(status_code=503, detail="Secure document storage is not configured.")
        self.cipher = Fernet(key.encode())
        self.directory = Path("private_uploads") / "booking_documents"
        self.directory.mkdir(parents=True, exist_ok=True)

    async def upload(self, document_request_id: str, founder_id: str, upload: UploadFile) -> AdvisorSharedDocument:
        content_type = upload.content_type or "application/octet-stream"
        if content_type not in self.allowed_types:
            raise HTTPException(status_code=422, detail="Only PDF, PNG, and JPEG documents are accepted.")
        raw = await upload.read()
        if not raw or len(raw) > self.max_bytes:
            raise HTTPException(status_code=422, detail="Document must be between 1 byte and 5 MB.")
        storage_key = f"{uuid4().hex}.bin"
        (self.directory / storage_key).write_bytes(self.cipher.encrypt(raw))
        record = AdvisorSharedDocument(
            document_request_id=document_request_id,
            founder_id=founder_id,
            storage_key=storage_key,
            original_name=(upload.filename or "document").replace("/", "_").replace("\\", "_"),
            content_type=content_type,
            size_bytes=len(raw),
            checksum=sha256(raw).hexdigest(),
        )
        self.session.add(record)
        return record

    def read(self, document: AdvisorSharedDocument) -> bytes:
        path = self.directory / document.storage_key
        if not path.exists():
            raise HTTPException(status_code=404, detail="The private document file is unavailable.")
        return self.cipher.decrypt(path.read_bytes())
