"""
Authentication and User models for Quant-Dash.

This module defines:
1. User database models with security fields
2. Authentication request/response schemas
3. User roles and permissions

Design decisions:
1. Separate user roles for different access levels (essential for financial platforms)
2. Email verification tracking (regulatory compliance)
3. Login attempt tracking (security monitoring)
4. Soft delete capability (data retention requirements)
"""

import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


# User Roles 
class UserRole(str, Enum):
    """
    User roles with hierarchical permissions.

    Why these roles:
    - ADMIN: Full system access (for platform operators)
    - TRADER: Full trading access (professional traders)
    - VIEWER: Read-only access (analysts, compliance)
    - PENDING: Unverified users (security requirement)
    """

    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"
    PENDING = "pending"


class UserStatus(str, Enum):
    """
    User account status for security and compliance.
    """

    ACTIVE = "active"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    PENDING_VERIFICATION = "pending_verification"


# Authentication Schemas
class UserLogin(BaseModel):
    """
    Login request schema with validation.

    Email as username is standard for financial platforms.
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128)


class UserRegister(BaseModel):

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

    @validator("password")
    def validate_password_strength(cls, v):
        """
        Enterprise password policy validation.

        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Ensure password confirmation matches."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class TokenResponse(BaseModel):

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token expiry in seconds")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    login_attempts: int
    locked_until: Optional[datetime]

    class Config:
        orm_mode = True


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @validator("new_password")
    def validate_password_strength(cls, v):
        return UserRegister.validate_password_strength(v)

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class EmailVerification(BaseModel):
    token: str = Field(..., description="Email verification token")


class RefreshTokenRequest(BaseModel):

    refresh_token: str = Field(..., description="Refresh token")


# Error Response Schemas
class AuthErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None


class ValidationErrorResponse(BaseModel):
    error: str = "validation_error"
    message: str
    details: List[dict]
