#!/usr/bin/env python3
"""
Authentication system test script for MindEase API.
Tests user registration, login, and JWT token functionality.
"""
import sys
import os
import json
import requests
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import UserCreate, UserLogin, Token
from jose import jwt
from app.core.config import settings


def test_password_hashing():
    """Test password hashing and verification."""
    print("🔐 Testing password hashing...")
    
    password = "test123password"
    hashed = get_password_hash(password)
    
    # Test correct password
    assert verify_password(password, hashed), "Password verification failed"
    print(f"  ✅ Password hashing: {len(hashed)} chars")
    
    # Test incorrect password
    assert not verify_password("wrongpassword", hashed), "Wrong password should not verify"
    print("  ✅ Wrong password correctly rejected")
    
    return True


def test_jwt_token_creation():
    """Test JWT token creation and validation."""
    print("🎫 Testing JWT token creation...")
    
    user_id = 123
    token = create_access_token(subject=user_id)
    
    # Decode token to verify contents
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload.get("sub") == str(user_id), "Token subject mismatch"
        assert "exp" in payload, "Token missing expiration"
        print(f"  ✅ Token created: {len(token)} chars")
        print(f"  ✅ Token payload: sub={payload.get('sub')}, exp={payload.get('exp')}")
        return token
    except Exception as e:
        print(f"  ❌ Token validation failed: {e}")
        return None


def test_schema_validation():
    """Test Pydantic schema validation."""
    print("📋 Testing schema validation...")
    
    # Test valid user creation
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "accept_terms": True,
            "is_active": True
        }
        user_create = UserCreate(**user_data)
        print("  ✅ Valid user creation schema")
    except Exception as e:
        print(f"  ❌ User creation schema failed: {e}")
        return False
    
    # Test password mismatch
    try:
        user_data["confirm_password"] = "different"
        UserCreate(**user_data)
        print("  ❌ Password mismatch should have failed")
        return False
    except Exception:
        print("  ✅ Password mismatch correctly rejected")
    
    # Test terms not accepted
    try:
        user_data["confirm_password"] = "password123"
        user_data["accept_terms"] = False
        UserCreate(**user_data)
        print("  ❌ Terms not accepted should have failed")
        return False
    except Exception:
        print("  ✅ Terms not accepted correctly rejected")
    
    # Test login schema
    try:
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        user_login = UserLogin(**login_data)
        print("  ✅ Valid login schema")
    except Exception as e:
        print(f"  ❌ Login schema failed: {e}")
        return False
    
    return True


def test_api_endpoints_mock():
    """Test API endpoints with mock data (no database required)."""
    print("🌐 Testing API endpoint logic...")
    
    # Test that we can import and instantiate the router
    try:
        from app.routers.auth import router
        print(f"  ✅ Auth router imported: {len(router.routes)} routes")
        
        # List all routes
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods) if route.methods else 'N/A'
                print(f"    - {methods} {route.path}")
        
    except Exception as e:
        print(f"  ❌ Router import failed: {e}")
        return False
    
    return True


def test_security_functions():
    """Test all security utility functions."""
    print("🛡️  Testing security functions...")
    
    try:
        from app.core.security import (
            verify_password, get_password_hash, create_access_token,
            check_user_role
        )
        
        # Test password functions
        password = "securepassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        print("  ✅ Password utilities working")
        
        # Test token creation
        token = create_access_token(subject=456)
        assert len(token) > 50  # JWT tokens are typically long
        print("  ✅ Token creation working")
        
        # Test role checking (mock user object)
        class MockRole:
            def __init__(self, name):
                self.name = name
        
        class MockUser:
            def __init__(self, roles):
                self.roles = [MockRole(role) for role in roles]
        
        admin_user = MockUser(["admin", "user"])
        regular_user = MockUser(["user"])
        
        assert check_user_role(admin_user, "admin")
        assert not check_user_role(regular_user, "admin")
        assert check_user_role(regular_user, "user")
        print("  ✅ Role checking working")
        
    except Exception as e:
        print(f"  ❌ Security functions failed: {e}")
        return False
    
    return True


def test_app_creation():
    """Test FastAPI app creation with auth routes."""
    print("🚀 Testing FastAPI app creation...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Check that app was created
        assert app is not None
        print("  ✅ FastAPI app created successfully")
        
        # Check that auth routes are included
        auth_routes = [route for route in app.routes if hasattr(route, 'path') and '/auth/' in route.path]
        print(f"  ✅ Auth routes found: {len(auth_routes)}")
        
        for route in auth_routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods) if route.methods else 'N/A'
                print(f"    - {methods} {route.path}")
        
    except Exception as e:
        print(f"  ❌ App creation failed: {e}")
        return False
    
    return True


def run_all_tests():
    """Run all authentication tests."""
    print("🧪 Starting MindEase Authentication System Tests")
    print("=" * 60)
    
    tests = [
        ("Password Hashing", test_password_hashing),
        ("JWT Token Creation", test_jwt_token_creation),
        ("Schema Validation", test_schema_validation),
        ("Security Functions", test_security_functions),
        ("API Endpoints", test_api_endpoints_mock),
        ("App Creation", test_app_creation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERROR - {e}")
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All authentication tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

