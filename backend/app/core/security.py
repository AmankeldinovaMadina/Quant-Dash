"""
Security utilities for Quant-Dash authentication system.

This module provides enterprise-grade security features:
- JWT token creation and validation
- Password hashing and verification
- Email verification tokens
- Security headers and middleware

Design decisions:
1. JWT with short expiry for access tokens (15 min) + refresh tokens (7 days)
   - Balances security (compromised tokens expire quickly) with UX
2. Bcrypt for password hashing with automatic salt generation
   - Industry standard, designed to be slow (prevents brute force)
3. Separate token types with different claims for fine-grained control
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from app.core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=settings.PWD_CONTEXT_SCHEMES,
    deprecated=settings.PWD_CONTEXT_DEPRECATED,
    bcrypt__rounds=12,
)


class SecurityManager:
    """
    Centralized security operations for the application.

    Why this approach:
    - Single responsibility for all security operations
    - Easy to audit and update security practices
    - Consistent token handling across the application
    """

    @staticmethod
    def create_access_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.utcnow(),
                "iss": settings.JWT_ISSUER,
                "aud": settings.JWT_AUDIENCE,
                "type": "access",
            }
        )

        return jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Create JWT refresh token with longer expiry.

        Longer expiry (7 days) for better UX, but contains minimal data.
        Used only for obtaining new access tokens.
        """
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "type": "refresh",
        }

        return jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def create_email_verification_token(email: str) -> str:
        """
        Create email verification token.

        Separate token type for email verification with 24h expiry.
        Cannot be used for API access - single purpose security.
        """
        expire = datetime.utcnow() + timedelta(
            hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS
        )

        to_encode = {
            "sub": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "type": "email_verification",
        }

        return jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def verify_token(
        token: str, expected_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Validates:
        - Token signature
        - Expiry time
        - Issuer and audience
        - Token type (prevents token substitution attacks)
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
            )

            if payload.get("type") != expected_type:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None
        except Exception:
            # Catch-all for unexpected errors
            return None

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.

        Bcrypt automatically:
        - Generates unique salt for each password
        - Uses configurable rounds (we use 12 = ~300ms)
        - Is designed to be slow (prevents brute force)
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Any error in verification = failed verification
            return False

    def create_password_reset_token(self, email: str) -> str:
        """
        Create a password reset token with expiration.

        Args:
            email: User email address

        Returns:
            JWT token containing email and expiration
        """
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        to_encode = {
            "sub": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "type": "password_reset",
        }

        try:
            return jwt.encode(
                to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
            )
        except Exception as e:
            raise ValueError(f"Failed to create password reset token: {str(e)}")

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """
        Verify and decode password reset token.

        Args:
            token: JWT password reset token

        Returns:
            Email address if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
                options={"verify_exp": True},
            )

            # Verify token type
            if payload.get("type") != "password_reset":
                return None

            email = payload.get("sub")
            if not email:
                return None

            return email

        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except (jwt.InvalidTokenError, ValueError):
            # Any error in verification = failed verification
            return None

    @staticmethod
    def generate_reset_token() -> str:
        """
        DEPRECATED: Use create_password_reset_token instead.

        This method is kept for backward compatibility but should be replaced
        with create_password_reset_token for proper expiration handling.
        """
        return secrets.token_urlsafe(32)


# Export singleton instance
security = SecurityManager()
