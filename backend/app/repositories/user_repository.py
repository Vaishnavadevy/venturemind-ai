"""SQLAlchemy persistence adapter for users and security tokens."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import SecurityTokenType
from app.models.user import SecurityToken, User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: str) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email.lower()))

    def add_user(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def add_token(self, token: SecurityToken) -> SecurityToken:
        self.session.add(token)
        self.session.flush()
        return token

    def get_active_token(
        self, token_hash: str, token_type: SecurityTokenType, now: datetime
    ) -> SecurityToken | None:
        statement = select(SecurityToken).where(
            SecurityToken.token_hash == token_hash,
            SecurityToken.token_type == token_type,
            SecurityToken.expires_at > now,
            SecurityToken.used_at.is_(None),
            SecurityToken.revoked_at.is_(None),
        )
        return self.session.scalar(statement)
