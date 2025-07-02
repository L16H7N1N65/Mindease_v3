#!/usr/bin/env python3
"""
Simple authentication test using pytest with in-memory SQLite.
Tests core authentication functionality without PostgreSQL dependencies.
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker



from app import create_app
from app.db.session import get_db


@pytest.fixture
def test_app():
    """
    Spin-up a FastAPI app backed by an in-memory SQLite DB.

    The trick is to import *all* model modules _before_
    calling `Base.metadata.create_all`, and to make sure the
    `chat` module (which registers the `messages` table)
    is imported before `rag_feedback` (which references it).
    """
    # 1. Engine + session
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # 2. Import every model module so its tables are attached to `Base.metadata`
    from app.db.models.base import Base
    from app.db.models import (
        auth,
        mood,
        document,
        social,
        organization,
        conversation,          
        rag_feedback,
        therapy,
    )
    # At this point *all* tables are registered on the same metadata object.

    # 3. Create the schema in one go
    Base.metadata.create_all(bind=engine)

    # 4. FastAPI dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_user_registration(client):
    """Test user registration."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    user_response = response.json()
    assert user_response["username"] == "testuser"
    assert user_response["email"] == "test@example.com"
    assert user_response["is_active"] is True
    assert "password" not in user_response  # Password should not be returned


def test_user_login(client):
    """Test user login."""
    # First register a user
    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # Now test login
    login_data = {
        "username": "login@example.com",  # Can use email as username
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token_response = response.json()
    assert "access_token" in token_response
    assert token_response["token_type"] == "bearer"
    assert len(token_response["access_token"]) > 50  # JWT tokens are long


def test_protected_endpoint(client):
    """Test protected endpoint access."""
    # Register and login to get token
    user_data = {
        "username": "protecteduser",
        "email": "protected@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    login_data = {
        "username": "protected@example.com",
        "password": "password123"
    }
    
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    
    # Test protected endpoint with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    user_info = response.json()
    assert user_info["username"] == "protecteduser"
    assert user_info["email"] == "protected@example.com"


def test_unauthorized_access(client):
    """Test unauthorized access to protected endpoint."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_duplicate_email_registration(client):
    """Test duplicate email registration."""
    user_data = {
        "username": "user1",
        "email": "duplicate@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    # First registration should succeed
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Second registration with same email should fail
    user_data["username"] = "user2"  # Different username, same email
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_duplicate_username_registration(client):
    """Test duplicate username registration."""
    user_data = {
        "username": "duplicateuser",
        "email": "user1@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    # First registration should succeed
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Second registration with same username should fail
    user_data["email"] = "user2@example.com"  # Different email, same username
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"].lower()


def test_invalid_login(client):
    """Test login with invalid credentials."""
    # Register a user first
    user_data = {
        "username": "validuser",
        "email": "valid@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "accept_terms": True,
        "is_active": True
    }
    
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # Test with wrong password
    login_data = {
        "username": "valid@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Incorrect email/username or password" in response.json()["detail"]


if __name__ == "__main__":
    # Run tests with pytest
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.exit(result.returncode)

