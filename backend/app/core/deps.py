"""
Authentication dependencies for FastAPI.

This module provides:
1. Token extraction and validation dependencies
2. User authentication dependencies
3. Role-based access control dependencies
4. Rate limiting dependencies

Why dependencies:
- Clean separation of concerns
- Reusable across endpoints
- Automatic OpenAPI documentation
- Easy testing and mocking
"""

from datetime import datetime, timedelta
from typing import Optional

import redis
from app.core.config import settings
from app.core.security import security
from app.models.auth import UserRole, UserStatus
from app.services.user import UserService
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Security scheme for OpenAPI documentation
security_scheme = HTTPBearer()


class AuthenticationError(HTTPException):
    """Custom authentication error with proper status codes."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error for insufficient permissions."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class RateLimitError(HTTPException):
    """Rate limit exceeded error."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """
    Extract and validate Bearer token from Authorization header.

    First step in our authentication chain.
    """
    if not credentials:
        raise AuthenticationError("Missing authentication token")

    if credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Invalid authentication scheme")

    return credentials.credentials


async def get_current_user_id(token: str = Depends(get_current_user_token)) -> int:
    """
    Validate token and extract user ID.
    """
    payload = security.verify_token(token, "access")

    if payload is None:
        raise AuthenticationError("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    try:
        return int(user_id)
    except ValueError:
        raise AuthenticationError("Invalid user identifier in token")


async def get_current_user(
    user_id: int = Depends(get_current_user_id), user_service: UserService = Depends()
) -> dict:
    """
    Get current authenticated user from database.

    This fetches the full user record and validates account status.
    """
    user = await user_service.get_user_by_id(user_id)

    if user is None:
        raise AuthenticationError("User not found")

    if user.get("status") == UserStatus.SUSPENDED:
        raise AuthenticationError("Account suspended")

    if user.get("status") == UserStatus.LOCKED:
        raise AuthenticationError("Account locked")

    if user.get("status") == UserStatus.PENDING_VERIFICATION:
        raise AuthenticationError("Email verification required")

    return user


async def get_verified_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get current user with email verification check.

    Some endpoints require verified email addresses.
    """
    if not current_user.get("is_email_verified"):
        raise AuthenticationError("Email verification required")

    return current_user


# Role-based access control dependencies
def require_role(required_role: UserRole):
    """
    Factory function for role-based access control.

    Usage: @app.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """

    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = UserRole(current_user.get("role"))

        # Role hierarchy: ADMIN > TRADER > VIEWER > PENDING
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.TRADER: 2,
            UserRole.VIEWER: 1,
            UserRole.PENDING: 0,
        }

        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        if user_level < required_level:
            raise AuthorizationError(f"Role '{required_role.value}' or higher required")

        return current_user

    return role_checker


# Admin-only access
require_admin = require_role(UserRole.ADMIN)

# Trader or admin access
require_trader = require_role(UserRole.TRADER)

# Any verified user access
require_verified = get_verified_user


class RateLimiter:
    """
    Rate limiting for authentication endpoints.

    Essential for preventing brute force attacks on login endpoints.
    Uses Redis with sliding window algorithm for distributed rate limiting.
    """

    def __init__(self, redis_client=None):
        """
        Initialize rate limiter with Redis client.

        Args:
            redis_client: Redis client instance. If None, rate limiting is disabled
                         (useful for development without Redis).
        """
        self.redis_client = redis_client

    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """
        Check if rate limit is exceeded using sliding window algorithm.

        Args:
            key: Unique identifier for the rate limit (e.g., IP address)
            limit: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        if not self.redis_client:
            # For development without Redis, allow all requests
            # In production, this should log a warning
            return True

        try:
            current_time = datetime.utcnow().timestamp()
            pipeline = self.redis_client.pipeline()

            # Remove old entries outside the window
            pipeline.zremrangebyscore(key, 0, current_time - window_seconds)

            # Count current requests in window
            pipeline.zcard(key)

            # Add current request
            pipeline.zadd(key, {str(current_time): current_time})

            # Set expiry on the key (cleanup)
            pipeline.expire(key, window_seconds + 60)  # Extra time for cleanup

            results = pipeline.execute()
            current_requests = results[1]

            return current_requests < limit

        except Exception as e:
            # If Redis fails, allow the request (fail open) but log the error
            # In production, you might want to use a circuit breaker pattern
            print(f"Rate limiting error: {e}")
            return True


# Redis connection dependency
def get_redis_client():
    """
    Get Redis client for rate limiting.

    Returns None if Redis is not available (development mode).
    """
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        # Test connection
        client.ping()
        return client
    except Exception:
        # Redis not available - return None for development mode
        return None


# Rate limiter dependency
def get_rate_limiter(redis_client=Depends(get_redis_client)) -> RateLimiter:
    """
    Get rate limiter with proper Redis client injection.
    """
    return RateLimiter(redis_client=redis_client)


async def login_rate_limit(
    request: Request, rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    """
    Rate limit for login attempts.

    Prevents brute force attacks: 5 attempts per IP per 15 minutes.
    """
    client_ip = request.client.host
    key = f"login_attempts:{client_ip}"

    is_allowed = await rate_limiter.check_rate_limit(
        key, 5, 900
    )  # 5 attempts in 15 minutes

    if not is_allowed:
        raise RateLimitError("Too many login attempts. Please try again later.")


async def registration_rate_limit(
    request: Request, rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    """
    Rate limit for registration attempts.

    Prevents spam registrations: 3 attempts per IP per hour.
    """
    client_ip = request.client.host
    key = f"registration_attempts:{client_ip}"

    is_allowed = await rate_limiter.check_rate_limit(
        key, 3, 3600
    )  # 3 attempts in 1 hour

    if not is_allowed:
        raise RateLimitError("Too many registration attempts. Please try again later.")
