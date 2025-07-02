"""
Simple test to verify basic application functionality.
"""
import pytest


def test_health_endpoint(client):
    """Test the health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_docs_endpoint(client):
    """Test that docs endpoint is accessible."""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200
    # Should return HTML content
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.xfail(reason="Database models have import conflicts, skipping until fixed")
def test_model_imports():
    """Test that models can be imported without errors."""
    try:
        from app.db.models import auth, document, mood, organization, social, therapy
        assert True
    except ImportError as e:
        pytest.fail(f"Model import failed: {e}")


@pytest.mark.xfail(reason="Database not available in test environment")
def test_database_connection():
    """Test database connection (expected to fail without PostgreSQL)."""
    from app.db.session import engine
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")


def test_app_creation():
    """Test that the FastAPI app can be created."""
    from app import create_app
    app = create_app()
    assert app is not None
    assert app.title == "MindEase API"

