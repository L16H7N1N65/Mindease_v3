import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import sys
sys.path.append(os.path.abspath("."))

# Import from the correct models location
from app.db.models.base import Base
from app.core.security import create_access_token, get_password_hash

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Import all models to ensure they're registered
    try:
        from app.db.models import auth, document, mood, organization, social, therapy
        Base.metadata.create_all(bind=engine)
    except ImportError as e:
        print(f"Warning: Could not import some models for testing: {e}")
    
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def seeded_db(db_engine):
    """Create a database session with test data."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    
    try:
        # Create minimal test data
        from app.db.models.auth import User, Role
        
        # Create a test role
        test_role = Role(name="test_user", description="Test user role")
        session.add(test_role)
        session.commit()
        
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            is_active=True,
            email_confirmed=True,
            terms_accepted=True
        )
        test_user.roles.append(test_role)
        session.add(test_user)
        session.commit()
        
        yield session
    except Exception as e:
        print(f"Warning: Could not create test data: {e}")
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client():
    """Create a test client without database dependency."""
    from main import app
    
    # Override database dependency to skip DB operations
    def override_get_db():
        return None
    
    from app.db.session import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
