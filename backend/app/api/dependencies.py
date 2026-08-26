"""Reusable FastAPI dependency providers."""

from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db_session
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthenticationError, AuthorizationError

DatabaseSession = Annotated[Session, Depends(get_db_session)]
bearer_scheme = HTTPBearer(auto_error=False)
TokenCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


def get_current_user(
    session: DatabaseSession,
    credentials: TokenCredentials,
) -> User:
    if not credentials:
        raise AuthenticationError("Authentication is required.")
    try:
        payload = decode_token(credentials.credentials, "access")
    except jwt.PyJWTError as error:
        raise AuthenticationError("Invalid or expired access token.") from error
    user = UserRepository(session).get_by_id(str(payload["sub"]))
    if not user or not user.is_active:
        raise AuthenticationError("Account is unavailable.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: UserRole):
    def role_checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise AuthorizationError("You do not have permission to perform this action.")
        return user

    return role_checker
