"""Authentication use cases, independent of HTTP transport."""

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

import jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.email import EmailSender, LoggingEmailSender
from app.core.exceptions import ConflictError, ResourceNotFoundError, VentureMindError
from app.core.security import create_token, decode_token, hash_password, hash_token, verify_password
from app.models.enums import SecurityTokenType
from app.models.user import SecurityToken, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPairResponse, UserResponse


class AuthenticationError(VentureMindError):
    status_code = 401
    code = "authentication_failed"


class AuthorizationError(VentureMindError):
    status_code = 403
    code = "authorization_failed"


class AuthService:
    def __init__(self, session: Session, email_sender: EmailSender | None = None) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.email_sender = email_sender or LoggingEmailSender()

    def register(self, full_name: str, email: str, password: str) -> User:
        normalized_email = email.lower()
        if self.users.get_by_email(normalized_email):
            raise ConflictError("An account with this email address already exists.")
        user = self.users.add_user(
            User(
                full_name=full_name.strip(),
                email=normalized_email,
                password_hash=hash_password(password),
            )
        )
        self._create_and_send_one_time_token(
            user,
            SecurityTokenType.EMAIL_VERIFICATION,
            "Verify your VentureMind AI email",
            "/verify-email?token=",
        )
        self.session.commit()
        self.session.refresh(user)
        return user

    def login(
        self, email: str, password: str, user_agent: str | None, ip_address: str | None
    ) -> TokenPairResponse:
        user = self.users.get_by_email(email)
        if not user or not user.is_active or user.is_archived or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        user.last_login_at = datetime.now(UTC)
        response = self._issue_token_pair(user, user_agent, ip_address)
        self.session.commit()
        return response

    def refresh(
        self, refresh_token: str, user_agent: str | None, ip_address: str | None
    ) -> TokenPairResponse:
        try:
            payload = decode_token(refresh_token, "refresh")
        except jwt.PyJWTError as error:
            raise AuthenticationError("Invalid or expired refresh token.") from error
        token = self.users.get_active_token(
            hash_token(refresh_token), SecurityTokenType.REFRESH, datetime.now(UTC)
        )
        if not token or token.user_id != payload["sub"]:
            raise AuthenticationError("Invalid or revoked refresh token.")
        user = self.users.get_by_id(token.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("Account is unavailable.")
        token.revoked_at = datetime.now(UTC)
        response = self._issue_token_pair(user, user_agent, ip_address)
        self.session.commit()
        return response

    def logout(self, refresh_token: str) -> None:
        token = self.users.get_active_token(
            hash_token(refresh_token), SecurityTokenType.REFRESH, datetime.now(UTC)
        )
        if token:
            token.revoked_at = datetime.now(UTC)
            self.session.commit()

    def verify_email(self, raw_token: str) -> None:
        token = self._consume_one_time_token(raw_token, SecurityTokenType.EMAIL_VERIFICATION)
        user = self.users.get_by_id(token.user_id)
        if not user:
            raise ResourceNotFoundError("User account was not found.")
        user.is_email_verified = True
        self.session.commit()

    def request_password_reset(self, email: str) -> None:
        user = self.users.get_by_email(email)
        if user and user.is_active:
            self._create_and_send_one_time_token(
                user,
                SecurityTokenType.PASSWORD_RESET,
                "Reset your VentureMind AI password",
                "/reset-password?token=",
            )
            self.session.commit()

    def reset_password(self, raw_token: str, new_password: str) -> None:
        token = self._consume_one_time_token(raw_token, SecurityTokenType.PASSWORD_RESET)
        user = self.users.get_by_id(token.user_id)
        if not user:
            raise ResourceNotFoundError("User account was not found.")
        user.password_hash = hash_password(new_password)
        self.session.commit()

    def _issue_token_pair(
        self, user: User, user_agent: str | None, ip_address: str | None
    ) -> TokenPairResponse:
        settings = get_settings()
        access, access_expiry = create_token(
            user.id, "access", timedelta(minutes=settings.jwt_access_token_expire_minutes)
        )
        refresh, refresh_expiry = create_token(
            user.id, "refresh", timedelta(days=settings.jwt_refresh_token_expire_days)
        )
        self.users.add_token(
            SecurityToken(
                user_id=user.id,
                token_type=SecurityTokenType.REFRESH,
                token_hash=hash_token(refresh),
                expires_at=refresh_expiry,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
        return TokenPairResponse(
            access_token=access,
            refresh_token=refresh,
            access_token_expires_at=access_expiry,
            refresh_token_expires_at=refresh_expiry,
            user=UserResponse.model_validate(user),
        )

    def _create_and_send_one_time_token(
        self, user: User, token_type: SecurityTokenType, subject: str, path_prefix: str
    ) -> None:
        raw_token = token_urlsafe(32)
        expiry = datetime.now(UTC) + timedelta(hours=24)
        self.users.add_token(
            SecurityToken(
                user_id=user.id,
                token_type=token_type,
                token_hash=hash_token(raw_token),
                expires_at=expiry,
            )
        )
        url = f"{get_settings().frontend_url}{path_prefix}{raw_token}"
        self.email_sender.send(user.email, subject, f"Use this link within 24 hours: {url}")

    def _consume_one_time_token(
        self, raw_token: str, token_type: SecurityTokenType
    ) -> SecurityToken:
        token = self.users.get_active_token(hash_token(raw_token), token_type, datetime.now(UTC))
        if not token:
            raise AuthenticationError("Invalid or expired token.")
        token.used_at = datetime.now(UTC)
        return token
