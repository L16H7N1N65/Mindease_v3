"""
Database session management for the MindEase API.
"""

import logging
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.db.models import __all__  
from app.core.config import settings
from app.db.models.base import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONNECTION_STRING = str(settings.SQLALCHEMY_DATABASE_URI)

# Create SQLAlchemy engine
engine = create_engine(
    DB_CONNECTION_STRING,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,      
    future=True,
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    """
    Get database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema(engine):
    """
    Ensure database schema is up to date.

    Args:
        engine: SQLAlchemy engine
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if "users" in existing_tables:
            logger.info("Database schema already exists, skipping migrations")
            return

        logger.info("Database schema not found, running Alembic migrations")
        try:
            import subprocess

            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd="/workspace/backend/mindease-api",
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info("Alembic migrations completed successfully")
            else:
                logger.error(f"Alembic migration failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to run Alembic migrations: {e}")
    except Exception as e:
        logger.warning(f"Database connection failed, skipping schema check: {e}")


def init_db(app=None):
    """
    Initialize database.

    Args:
        app: Optional FastAPI application
    """
    # Import models to ensure they are registered with the Base
    # Import these inside the function to avoid circular imports
    try:
        from app.db.models import __all__

        logger.info("Models imported successfully")
    except ImportError as e:
        logger.warning(f"Could not import some models: {e}")

    # Ensure schema is up to date (gracefully handle DB connection failures)
    try:
        ensure_schema(engine)

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(
            f"Database initialization failed (PostgreSQL may not be running): {e}"
        )
        logger.info("Application will continue without database functionality")
