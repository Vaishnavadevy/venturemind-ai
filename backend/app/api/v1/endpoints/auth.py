"""Public and authenticated account endpoints."""

from fastapi import APIRouter, Request, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.auth import (
    EmailVerificationRequest,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserResponse,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")


def client_metadata(request: Request) -> tuple[str | None, str | None]:
    return request.headers.get("user-agent"), request.client.host if request.client else None


@router.post(
    "/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, session: DatabaseSession) -> APIResponse[UserResponse]:
    user = AuthService(session).register(payload.full_name, str(payload.email), payload.password)
    return APIResponse(
        data=UserResponse.model_validate(user),
        message="Registration successful. Check your email to verify your account.",
    )


@router.post("/login", response_model=APIResponse[TokenPairResponse])
def login(
    payload: LoginRequest, request: Request, session: DatabaseSession
) -> APIResponse[TokenPairResponse]:
    agent, address = client_metadata(request)
    return APIResponse(
        data=AuthService(session).login(str(payload.email), payload.password, agent, address)
    )


@router.get("/me", response_model=APIResponse[UserResponse])
def get_me(user: CurrentUser) -> APIResponse[UserResponse]:
    return APIResponse(data=UserResponse.model_validate(user))


@router.post("/refresh", response_model=APIResponse[TokenPairResponse])
def refresh(
    payload: RefreshRequest, request: Request, session: DatabaseSession
) -> APIResponse[TokenPairResponse]:
    agent, address = client_metadata(request)
    return APIResponse(data=AuthService(session).refresh(payload.refresh_token, agent, address))


@router.post("/logout", response_model=APIResponse[None])
def logout(payload: RefreshRequest, session: DatabaseSession) -> APIResponse[None]:
    AuthService(session).logout(payload.refresh_token)
    return APIResponse(data=None, message="You have been signed out.")


@router.post("/verify-email", response_model=APIResponse[None])
def verify_email(payload: EmailVerificationRequest, session: DatabaseSession) -> APIResponse[None]:
    AuthService(session).verify_email(payload.token)
    return APIResponse(data=None, message="Email address verified.")


@router.post("/forgot-password", response_model=APIResponse[None])
def forgot_password(payload: PasswordResetRequest, session: DatabaseSession) -> APIResponse[None]:
    AuthService(session).request_password_reset(str(payload.email))
    return APIResponse(
        data=None, message="If an account exists, password reset instructions have been sent."
    )


@router.post("/reset-password", response_model=APIResponse[None])
def reset_password(
    payload: PasswordResetConfirmRequest, session: DatabaseSession
) -> APIResponse[None]:
    AuthService(session).reset_password(payload.token, payload.new_password)
    return APIResponse(data=None, message="Password updated successfully.")
