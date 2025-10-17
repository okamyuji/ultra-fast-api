"""Alembic environment configuration."""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Logging configuration
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to None (manual migrations)
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    sqlalchemy_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    # Use psycopg2 for migrations (sync driver)
    sqlalchemy_url = sqlalchemy_url.replace("postgresql+asyncpg://", "postgresql://")

    context.configure(
        url=sqlalchemy_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    sqlalchemy_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    # Use psycopg2 for migrations (sync driver)
    sqlalchemy_url = sqlalchemy_url.replace("postgresql+asyncpg://", "postgresql://")

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = sqlalchemy_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
