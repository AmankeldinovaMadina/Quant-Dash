"""
User service layer for Quant-Dash authentication.

This module handles:
1. User creation and management
2. Authentication logic
3. Email verification
4. Password reset functionality

Why service layer:
- Separates business logic from API endpoints
- Makes testing easier (mock services vs mock databases)
- Centralizes user-related operations
- Easier to maintain and modify business rules
"""

import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.security import security
from app.models.auth import (
    PasswordReset,
    PasswordResetConfirm,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserRole,
    UserStatus,
)


class UserService:
    """
    User service for authentication and user management.

    In production, this would interact with a database ORM.
    For now, we'll use placeholder methods that show the structure.
    """

    def __init__(self):
        # In production, inject database dependency here
        pass

    async def register_user(self, user_data: UserRegister) -> Dict[str, Any]:
        """
        Register a new user with comprehensive validation.

        Process:
        1. Check if email already exists
        2. Hash password securely
        3. Create user record
        4. Send verification email
        5. Return user data (excluding sensitive info)
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash password using bcrypt
        hashed_password = security.hash_password(user_data.password)

        # Create user record (placeholder - in production use ORM)
        user_record = {
            "email": user_data.email,
            "password_hash": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "role": UserRole.PENDING,  # Start as pending until verified
            "status": UserStatus.PENDING_VERIFICATION,
            "is_email_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "login_attempts": 0,
            "locked_until": None,
        }

        # Save to database (placeholder)
        # user = await self.db.create_user(user_record)

        # Send verification email
        await self.send_verification_email(user_data.email)

        # Return user data (exclude sensitive information)
        return {
            "id": 1,  # Placeholder
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "role": UserRole.PENDING,
            "status": UserStatus.PENDING_VERIFICATION,
            "is_email_verified": False,
            "created_at": datetime.utcnow(),
        }

    async def authenticate_user(
        self, login_data: UserLogin
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials with security checks.

        Security measures:
        1. Account lockout after failed attempts
        2. Constant-time password verification
        3. Status checks (suspended, locked, etc.)
        4. Login attempt tracking
        """
        user = await self.get_user_by_email(login_data.email)
        if not user:
            return None

        # Check if account is locked
        if user.get("locked_until") and user["locked_until"] > datetime.utcnow():
            raise ValueError(
                "Account temporarily locked due to multiple failed login attempts"
            )

        # Verify password
        if not security.verify_password(login_data.password, user["password_hash"]):
            # Increment failed login attempts
            await self.increment_login_attempts(user["id"])
            return None

        # Reset login attempts on successful login
        await self.reset_login_attempts(user["id"])

        # Update last login time
        await self.update_last_login(user["id"])

        return user

    async def create_tokens(self, user: Dict[str, Any]) -> TokenResponse:
        """
        Create access and refresh tokens for authenticated user.

        Returns both tokens with proper expiry information.
        """
        # Create access token with user claims
        access_token_data = {
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "verified": user["is_email_verified"],
        }

        access_token = security.create_access_token(access_token_data)
        refresh_token = security.create_refresh_token(user["id"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Create new access token using refresh token.

        Validates refresh token and issues new access token.
        """
        payload = security.verify_token(refresh_token, "refresh")
        if not payload:
            raise ValueError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid refresh token payload")

        user = await self.get_user_by_id(int(user_id))
        if not user:
            raise ValueError("User not found")

        return await self.create_tokens(user)

    async def verify_email(self, token: str) -> bool:
        """
        Verify user email using verification token.

        Promotes user from PENDING to VIEWER role after verification.
        """
        payload = security.verify_token(token, "email_verification")
        if not payload:
            return False

        email = payload.get("sub")
        if not email:
            return False

        user = await self.get_user_by_email(email)
        if not user:
            return False

        # Update user verification status
        await self.update_user_verification(user["id"], True)

        # Promote from PENDING to VIEWER role
        if user["role"] == UserRole.PENDING:
            await self.update_user_role(user["id"], UserRole.VIEWER)

        return True

    async def send_verification_email(self, email: str) -> bool:
        """
        Send email verification link to user.

        Creates verification token and sends email with link.
        """
        verification_token = security.create_email_verification_token(email)
        verification_link = (
            f"{settings.SERVER_HOST}/verify-email?token={verification_token}"
        )

        # Email content
        subject = "Verify your Quant-Dash account"
        body = f"""
        Welcome to Quant-Dash!
        
        Please click the link below to verify your email address:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create this account, please ignore this email.
        """

        return await self.send_email(email, subject, body)

    async def initiate_password_reset(self, email: str) -> bool:
        """
        Initiate password reset process.

        Sends password reset email with secure token.
        """
        user = await self.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists (security best practice)
            return True

        reset_token = security.generate_reset_token()

        # Store reset token in database with expiry (placeholder)
        # await self.store_reset_token(user["id"], reset_token)

        reset_link = f"{settings.SERVER_HOST}/reset-password?token={reset_token}"

        subject = "Password Reset - Quant-Dash"
        body = f"""
        A password reset was requested for your Quant-Dash account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        """

        return await self.send_email(email, subject, body)

    # Placeholder database methods (implement with actual ORM)
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        # Placeholder - implement with database query
        return None

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        # Placeholder - implement with database query
        return None

    async def increment_login_attempts(self, user_id: int) -> None:
        """Increment failed login attempts counter."""
        # Placeholder - implement with database update
        pass

    async def reset_login_attempts(self, user_id: int) -> None:
        """Reset login attempts counter."""
        # Placeholder - implement with database update
        pass

    async def update_last_login(self, user_id: int) -> None:
        """Update last login timestamp."""
        # Placeholder - implement with database update
        pass

    async def update_user_verification(self, user_id: int, verified: bool) -> None:
        """Update user email verification status."""
        # Placeholder - implement with database update
        pass

    async def update_user_role(self, user_id: int, role: UserRole) -> None:
        """Update user role."""
        # Placeholder - implement with database update
        pass

    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email using SMTP.

        In production, use a proper email service like SendGrid or AWS SES.
        """
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            # Email not configured - log the email content for development
            print(f"Email to {to_email}: {subject}\n{body}")
            return True

        try:
            msg = MIMEMultipart()
            msg["From"] = settings.EMAILS_FROM_EMAIL
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_TLS:
                server.starttls()

            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            # Log error in production
            print(f"Email sending failed: {e}")
            return False
