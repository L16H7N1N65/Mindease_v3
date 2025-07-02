#!/usr/bin/env python3
"""
Integration test for MindEase API with SQLite in-memory database.
Tests the complete authentication flow with a real database.
"""
import sys
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.db.models.base import Base
from app.db.session import get_db


def test_with_sqlite():
    """Test authentication with SQLite in-memory database."""
    print("🗄️  Testing with SQLite in-memory database...")
    
    # Create SQLite in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("  ✅ SQLite database and tables created")
    
    # Override the get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Create app and override database
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    print("  ✅ Health endpoint working")
    
    # Test user registration
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    print(f"  📝 Registration response: {response.status_code}")
    
    if response.status_code == 201:
        user_response = response.json()
        print(f"  ✅ User registered: {user_response.get('username')} ({user_response.get('email')})")
        user_id = user_response.get('id')
    else:
        print(f"  ❌ Registration failed: {response.text}")
        return False
    
    # Test user login
    login_data = {
        "username": "test@example.com",  # Can use email as username
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    print(f"  🔑 Login response: {response.status_code}")
    
    if response.status_code == 200:
        token_response = response.json()
        access_token = token_response.get("access_token")
        print(f"  ✅ Login successful, token: {access_token[:20]}...")
    else:
        print(f"  ❌ Login failed: {response.text}")
        return False
    
    # Test protected endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    print(f"  👤 Protected endpoint response: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"  ✅ Protected endpoint working: {user_info.get('username')}")
    else:
        print(f"  ❌ Protected endpoint failed: {response.text}")
        return False
    
    # Test unauthorized access
    response = client.get("/api/v1/auth/me")
    print(f"  🚫 Unauthorized access response: {response.status_code}")
    
    if response.status_code == 401:
        print("  ✅ Unauthorized access correctly rejected")
    else:
        print(f"  ❌ Unauthorized access should return 401, got {response.status_code}")
        return False
    
    print("  🎉 All integration tests passed!")
    return True


def test_duplicate_registration():
    """Test duplicate user registration handling."""
    print("🔄 Testing duplicate registration...")
    
    # Create SQLite in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Override the get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Create app and override database
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    client = TestClient(app)
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    # First registration should succeed
    response = client.post("/api/v1/auth/register", json=user_data)
    if response.status_code != 201:
        print(f"  ❌ First registration failed: {response.text}")
        return False
    print("  ✅ First registration successful")
    
    # Second registration with same email should fail
    response = client.post("/api/v1/auth/register", json=user_data)
    if response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "already registered" in error_detail.lower():
            print("  ✅ Duplicate email correctly rejected")
        else:
            print(f"  ❌ Wrong error message: {error_detail}")
            return False
    else:
        print(f"  ❌ Duplicate registration should return 400, got {response.status_code}")
        return False
    
    # Registration with same username but different email should fail
    user_data["email"] = "different@example.com"
    response = client.post("/api/v1/auth/register", json=user_data)
    if response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "already taken" in error_detail.lower():
            print("  ✅ Duplicate username correctly rejected")
        else:
            print(f"  ❌ Wrong error message: {error_detail}")
            return False
    else:
        print(f"  ❌ Duplicate username should return 400, got {response.status_code}")
        return False
    
    return True


def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Starting MindEase Authentication Integration Tests")
    print("=" * 60)
    
    tests = [
        ("SQLite Integration", test_with_sqlite),
        ("Duplicate Registration", test_duplicate_registration),
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
    print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("⚠️  Some integration tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)

