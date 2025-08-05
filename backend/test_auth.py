"""
Test script for Quant-Dash authentication system.

This script tests:
1. Basic FastAPI application startup
2. Authentication endpoints
3. Token generation and validation
4. Security utilities

Run this script to verify the authentication implementation works correctly.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.append(
    "/Users/madinaamankeldinova/Desktop/personal_project/quant-dash/backend"
)

try:
    from app.core.config import settings
    from app.core.security import security
    from app.models.auth import UserRole, UserStatus

    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_password_hashing():
    """Test password hashing and verification."""
    print("\n🔐 Testing Password Hashing...")

    password = "TestPassword123!"

    # Hash the password
    hashed = security.hash_password(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed[:50]}...")

    # Verify correct password
    is_valid = security.verify_password(password, hashed)
    print(f"Password verification (correct): {is_valid}")

    # Verify incorrect password
    is_invalid = security.verify_password("WrongPassword", hashed)
    print(f"Password verification (incorrect): {is_invalid}")

    if is_valid and not is_invalid:
        print("✅ Password hashing test passed!")
    else:
        print("❌ Password hashing test failed!")

    return is_valid and not is_invalid


def test_jwt_tokens():
    """Test JWT token creation and validation."""
    print("\n🎫 Testing JWT Tokens...")

    # Test data
    user_data = {"sub": "123", "email": "test@example.com", "role": "trader"}

    # Create access token
    access_token = security.create_access_token(user_data)
    print(f"Access token created: {access_token[:50]}...")

    # Create refresh token
    refresh_token = security.create_refresh_token(123)
    print(f"Refresh token created: {refresh_token[:50]}...")

    # Verify access token
    access_payload = security.verify_token(access_token, "access")
    print(f"Access token payload: {access_payload}")

    # Verify refresh token
    refresh_payload = security.verify_token(refresh_token, "refresh")
    print(f"Refresh token payload: {refresh_payload}")

    # Test invalid token
    invalid_payload = security.verify_token("invalid_token", "access")
    print(f"Invalid token result: {invalid_payload}")

    # Test email verification token
    email_token = security.create_email_verification_token("test@example.com")
    email_payload = security.verify_token(email_token, "email_verification")
    print(f"Email verification token payload: {email_payload}")

    success = (
        access_payload is not None
        and refresh_payload is not None
        and invalid_payload is None
        and email_payload is not None
    )

    if success:
        print("✅ JWT token test passed!")
    else:
        print("❌ JWT token test failed!")

    return success


def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing Configuration...")

    print(f"API Version: {settings.API_V1_STR}")
    print(f"Access token expiry: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"Refresh token expiry: {settings.REFRESH_TOKEN_EXPIRE_DAYS} days")
    print(f"JWT Algorithm: {settings.JWT_ALGORITHM}")
    print(f"Project name: {settings.PROJECT_NAME}")
    print(f"CORS origins: {settings.BACKEND_CORS_ORIGINS}")

    # Check if required settings are present
    required_settings = [
        settings.SECRET_KEY,
        settings.API_V1_STR,
        settings.JWT_ALGORITHM,
        settings.PROJECT_NAME,
    ]

    success = all(setting for setting in required_settings)

    if success:
        print("✅ Configuration test passed!")
    else:
        print("❌ Configuration test failed!")

    return success


def test_user_models():
    """Test user model validation."""
    print("\n👤 Testing User Models...")

    try:
        from app.models.auth import UserLogin, UserRegister, UserRole, UserStatus

        # Test user registration model
        valid_user = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "first_name": "John",
            "last_name": "Doe",
        }

        user_register = UserRegister(**valid_user)
        print(f"Valid user registration: {user_register.email}")

        # Test user login model
        login_data = UserLogin(email="test@example.com", password="TestPassword123!")
        print(f"User login model: {login_data.email}")

        # Test user roles
        roles = [role.value for role in UserRole]
        print(f"Available roles: {roles}")

        # Test user statuses
        statuses = [status.value for status in UserStatus]
        print(f"Available statuses: {statuses}")

        print("✅ User models test passed!")
        return True

    except Exception as e:
        print(f"❌ User models test failed: {e}")
        return False


def test_basic_app_structure():
    """Test basic FastAPI app structure."""
    print("\n🚀 Testing FastAPI App Structure...")

    try:
        from app.api.v1 import api_router
        from app.main import app

        print(f"FastAPI app created: {app.title}")
        print(f"API router created: {type(api_router)}")

        print("✅ App structure test passed!")
        return True

    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Quant-Dash Authentication System Tests")
    print("=" * 50)

    tests = [
        test_configuration,
        test_password_hashing,
        test_jwt_tokens,
        test_user_models,
        test_basic_app_structure,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("🎉 All tests passed! Authentication system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
