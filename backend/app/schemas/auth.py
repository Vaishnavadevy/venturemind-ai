"""Authentication request and response contracts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr = Field(max_length=191)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=191)
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(max_length=191)


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(min_length=20)
    new_password: str = Field(min_length=12, max_length=128)


class EmailVerificationRequest(BaseModel):
    token: str = Field(min_length=20)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_email_verified: bool
    created_at: datetime


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    user: UserResponse
