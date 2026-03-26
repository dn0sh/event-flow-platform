from logging.config import fileConfig
from urllib.parse import quote_plus

from sqlalchemy import engine_from_config, pool

from alembic import context
from src.config.settings import get_settings
from src.models.order import Base

config = context.config
target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_sync_url() -> str:
    """Синхронный DSN для Alembic (psycopg2); asyncpg для приложения не подходит."""
    s = get_settings()
    return (
        f"postgresql+psycopg2://{quote_plus(s.postgres_user)}:{quote_plus(s.postgres_password)}"
        f"@{s.postgres_host}:{s.postgres_port}/{s.postgres_db}"
    )


def run_migrations_offline() -> None:
    url = get_sync_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = dict(config.get_section(config.config_ini_section) or {})
    configuration["sqlalchemy.url"] = get_sync_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
