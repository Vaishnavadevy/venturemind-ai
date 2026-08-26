"""Password hashing, signed JWTs, and opaque-token hashing."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Literal
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hasher = PasswordHash.recommended()
TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def hash_token(token: str) -> str:
    """Store a non-reversible token fingerprint in the database."""
    return sha256(token.encode("utf-8")).hexdigest()


def create_token(
    subject: str, token_type: TokenType, expires_delta: timedelta
) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = datetime.now(UTC) + expires_delta
    payload = {"sub": subject, "type": token_type, "jti": str(uuid4()), "exp": expires_at}
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    ), expires_at


def decode_token(token: str, expected_type: TokenType) -> dict[str, object]:
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != expected_type or not isinstance(payload.get("sub"), str):
        raise jwt.InvalidTokenError("Invalid token type.")
    return payload
