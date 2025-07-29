from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
from dotenv import load_dotenv
from app.core.settings import Settings  # adjust path if needed
import app.db.base 
from app.db.declarative_base import Base  # declarative_base with metadata

# Load .env
load_dotenv()


def include_object(object, name, type_, reflected, compare_to):
    # Exclude unmanaged tables from Alembic's autogenerate
    if type_ == "table" and name in {"planet_osm_point", "planet_osm_polygon", "planet_osm_line", "spatial_ref_sys", 
                                     "planet_osm_roads", "planet_osm_rels", "planet_osm_ways", "planet_osm_nodes"}: 
        return False
    return True


# Load Settings
settings = Settings()

# Alembic Config object
config = context.config

# Inject the sync DB URL from our app settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNCH)

# Set up logging from .ini if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata used for 'autogenerate' migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB engine, just emits SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connect to DB and execute)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


# Dispatch mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
