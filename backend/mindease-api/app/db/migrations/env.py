"""
Alembic environment configuration.
"""

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.models import Base

# --------------------------------------------------------------------------- #
# Alembic Config + logging
# --------------------------------------------------------------------------- #
config = context.config
fileConfig(config.config_file_name)

# Tell Alembic which metadata to autogenerate migrations from.
target_metadata = Base.metadata

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _resolve_database_url() -> str:
    """
    Return a plain-string SQLAlchemy URL.

    Priority:
    1. `DATABASE_URL` env var (container-friendly).
    2. `settings.SQLALCHEMY_DATABASE_URI` built by Pydantic.
    """
    url = os.getenv("DATABASE_URL") or settings.SQLALCHEMY_DATABASE_URI
    if not url:
        raise RuntimeError(
            "DATABASE_URL (or SQLALCHEMY_DATABASE_URI) is missing; "
            "Alembic cannot run migrations."
        )
    return str(url)  # Cast MultiHostUrl / PostgresDsn → str


# --------------------------------------------------------------------------- #
# Offline mode
# --------------------------------------------------------------------------- #
def run_migrations_offline() -> None:
    """Run migrations without a live DB connection."""
    url = _resolve_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------------------------------- #
# Online mode
# --------------------------------------------------------------------------- #
def run_migrations_online() -> None:
    """Run migrations with an Engine & live connection."""
    url = _resolve_database_url()

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # no pool reuse during migrations
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()