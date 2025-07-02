import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.models.models import User
from app.core.security import get_password_hash

# point our test suite at an in-memory SQLite database
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

BASE = settings.API_V1_STR            # e.g. "/api/v1"
AUTH = f"{BASE}/auth"

class TestAuthRoutes:
    @pytest.mark.parametrize("payload", [
        {},  # completely empty
        {"email": "", "password": "", "confirm_password": "", "accept_terms": False},
        {"email": "test@test.com", "password": "short", "confirm_password": "short", "accept_terms": True},
        {"email": "test@test.com", "password": "Mismatch1!", "confirm_password": "NoMatch!2", "accept_terms": True},
        {"email": "test@test.com", "password": "ValidPass1!", "confirm_password": "ValidPass1!", "accept_terms": False},
    ])
    def test_register_validation(self, client: TestClient, payload):
        # invalid payload → 422
        resp = client.post(f"{AUTH}/register", json=payload)
        assert resp.status_code == 422
        body = resp.json()
        assert "detail" in body

    def test_register_user(self, client: TestClient, db_session):
        """Test successful user registration."""
        user_data = {
            "email": "newregister@example.com",
            "password": "securePassword!1",
            "confirm_password": "securePassword!1",
            "accept_terms": True,
        }

        resp = client.post(f"{AUTH}/register", json=user_data)
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["email"] == user_data["email"]
        assert isinstance(data["created_at"], str)
        assert data["is_verified"] is False
        assert data["account_status"] == "active"

        # verify in database
        db_user = db_session.query(User).filter_by(email=user_data["email"]).first()
        assert db_user is not None

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with an email that already exists."""
        payload = {
            "email": test_user.email,
            "password": "AnotherPass!2",
            "confirm_password": "AnotherPass!2",
            "accept_terms": True,
        }
        resp = client.post(f"{AUTH}/register", json=payload)
        assert resp.status_code == 400
        body = resp.json()
        assert "detail" in body
        assert "already registered" in body["detail"].lower()

    def test_login_success(self, client: TestClient, test_user, test_token):
        """Test successful login returns only token fields."""
        form = {
            "username": test_user.email,
            "password": "password123!"
        }
        resp = client.post(f"{AUTH}/login", data=form)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user):
        form = {"username": test_user.email, "password": "bad"}
        resp = client.post(f"{AUTH}/login", data=form)
        assert resp.status_code == 401
        body = resp.json()
        assert "detail" in body
        assert "incorrect email or password" in body["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        form = {"username": "missing@example.com", "password": "whatever"}
        resp = client.post(f"{AUTH}/login", data=form)
        assert resp.status_code == 401
        assert "detail" in resp.json()

    def test_login_inactive_user(self, client: TestClient, db_session):
        # create an inactive user with a known password
        inactive = User(
            email="inactive@example.com",
            password_hash=get_password_hash("password123!"),
            is_active=False,
            created_at=datetime.utcnow(),
        )
        db_session.add(inactive)
        db_session.commit()

        form = {"username": inactive.email, "password": "password123!"}
        resp = client.post(f"{AUTH}/login", data=form)
        assert resp.status_code == 400
        assert resp.json()["detail"].lower() == "inactive user"

    def test_password_reset_request(self, client: TestClient):
        """Endpoint always returns 200 and a message."""
        resp = client.post(
            f"{AUTH}/password-reset/request",
            json={"email": "anything@example.com"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "message" in body
        assert "reset link" in body["message"].lower()

    def test_password_reset_confirm(self, client: TestClient):
        resp = client.post(
            f"{AUTH}/password-reset/confirm",
            json={"token": "xyz", "new_password": "NewPass!3"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "message" in body
        assert "successfully reset" in body["message"].lower()

    def test_refresh_and_logout(self, client: TestClient, test_token: str):
        # refresh
        refresh = client.post(
            f"{AUTH}/refresh",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert refresh.status_code == 200
        rdata = refresh.json()
        assert "access_token" in rdata and rdata["token_type"] == "bearer"

        # logout
        logout = client.post(
            f"{AUTH}/logout",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert logout.status_code == 200
        ldata = logout.json()
        assert "message" in ldata
        assert "successfully logged out" in ldata["message"].lower()
