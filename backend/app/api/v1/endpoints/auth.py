"""
Authentication endpoints for Quant-Dash API.

This module provides:
1. User registration and login
2. Token refresh
3. Email verification
4. Password reset
5. User profile management

Design principles:
- Clear error messages without security leaks
- Proper HTTP status codes
- Rate limiting on sensitive endpoints
- Comprehensive input validation
"""

from app.core.deps import (
    get_current_user,
    login_rate_limit,
    registration_rate_limit,
    require_verified,
)
from app.models.auth import (
    AuthErrorResponse,
    EmailVerification,
    PasswordReset,
    PasswordResetConfirm,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.user import UserService
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(registration_rate_limit)],
    summary="Register new user",
    description="Register a new user account with email verification required",
)
async def register(user_data: UserRegister, user_service: UserService = Depends()):
    """
    Register a new user account.

    This endpoint:
    1. Validates input data (password strength, email format)
    2. Checks for duplicate email addresses
    3. Creates user account with PENDING status
    4. Sends email verification link
    5. Returns user data (excluding sensitive information)

    Rate limited to prevent spam registrations.
    """
    try:
        user = await user_service.register_user(user_data)
        return UserResponse(**user)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log the actual error but don't expose it
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(login_rate_limit)],
    summary="User login",
    description="Authenticate user and return access and refresh tokens",
)
async def login(login_data: UserLogin, user_service: UserService = Depends()):
    """
    Authenticate user and return tokens.

    This endpoint:
    1. Validates credentials
    2. Checks account status (not locked, suspended, etc.)
    3. Tracks login attempts for security
    4. Returns JWT access and refresh tokens

    Rate limited to prevent brute force attacks.
    """
    try:
        user = await user_service.authenticate_user(login_data)

        if not user:
            # Generic error message to prevent user enumeration
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        tokens = await user_service.create_tokens(user)
        return tokens

    except ValueError as e:
        # Handle specific errors like account lockout
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again.",
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token",
)
async def refresh_token(
    refresh_data: RefreshTokenRequest, user_service: UserService = Depends()
):
    """
    Refresh access token using refresh token.

    This endpoint:
    1. Validates refresh token
    2. Checks if user still exists and is active
    3. Issues new access token
    4. Returns new token pair
    """
    try:
        tokens = await user_service.refresh_access_token(refresh_data.refresh_token)
        return tokens

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please login again.",
        )


@router.post(
    "/verify-email",
    summary="Verify email address",
    description="Verify user email address using verification token",
)
async def verify_email(
    verification_data: EmailVerification, user_service: UserService = Depends()
):
    """
    Verify user email address.

    This endpoint:
    1. Validates verification token
    2. Updates user verification status
    3. Promotes user role from PENDING to VIEWER
    """
    try:
        success = await user_service.verify_email(verification_data.token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        return {"message": "Email verified successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again.",
        )


@router.post(
    "/password-reset",
    summary="Request password reset",
    description="Send password reset email to user",
)
async def request_password_reset(
    reset_data: PasswordReset, user_service: UserService = Depends()
):
    """
    Request password reset.

    This endpoint:
    1. Finds user by email (if exists)
    2. Generates secure reset token
    3. Sends password reset email
    4. Returns success regardless of email existence (security)
    """
    try:
        await user_service.initiate_password_reset(reset_data.email)

        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}

    except Exception as e:
        # Still return success message for security
        return {"message": "If the email exists, a password reset link has been sent"}


@router.post(
    "/password-reset/confirm",
    summary="Confirm password reset",
    description="Reset password using reset token",
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm, user_service: UserService = Depends()
):
    """
    Confirm password reset with new password.

    This endpoint:
    1. Validates reset token
    2. Validates new password strength
    3. Updates user password
    4. Invalidates reset token
    """
    # Implementation would go here
    # For now, return placeholder response
    return {"message": "Password reset functionality to be implemented"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get current authenticated user's profile information",
)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile.

    This endpoint:
    1. Validates authentication token
    2. Returns user profile information
    3. Excludes sensitive data (password hash, etc.)
    """
    return UserResponse(**current_user)


@router.post(
    "/logout",
    summary="User logout",
    description="Logout user (client should discard tokens)",
)
async def logout():
    """
    Logout user.

    Since we use stateless JWT tokens, logout is primarily client-side.
    In production, you might want to:
    1. Add token to blacklist (if using Redis)
    2. Log the logout event
    3. Clear any server-side sessions
    """
    return {"message": "Logged out successfully"}


@router.get(
    "/protected",
    dependencies=[Depends(require_verified)],
    summary="Protected endpoint example",
    description="Example endpoint that requires verified email",
)
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Example protected endpoint.

    This demonstrates how to protect endpoints with different requirements:
    - Authentication required
    - Email verification required
    - Specific roles required (see role-based examples)
    """
    return {
        "message": f"Hello {current_user['first_name']}, this is a protected endpoint!",
        "user_role": current_user["role"],
        "email_verified": current_user["is_email_verified"],
    }
