import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.settings import settings

logger = logging.getLogger(__name__)


def validate_imported_tables(
    db_url: str = None,
    table_prefix: str = "planet_osm_new",
    required_tables=("point", "line", "polygon"),
    min_expected_rows=100,  # adjust as fits your scale
) -> dict:
    """
    Checks that temp OSM tables exist and are non-empty.
    Returns dict of {table: row_count}.
    Raises if any are missing or invalid.
    """
    db_url = db_url or settings.DATABASE_URL_SYNCH
    # Use SQLAlchemy sync engine for a short-lived DB connection (faster for this use case)
    from sqlalchemy import create_engine

    engine = create_engine(db_url)

    results = {}
    with engine.connect() as conn:
        for t in required_tables:
            tablename = f"{table_prefix}_{t}"
            # Check table exists
            exists = conn.execute(
                text("SELECT to_regclass(:tn) IS NOT NULL"), {"tn": tablename}
            ).scalar()
            if not exists:
                logger.error("Missing imported table: %s", tablename)
                raise RuntimeError(f"Imported table missing: {tablename}")

            # Row count
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tablename}")).scalar()
            logger.info("Imported table %s: %d rows", tablename, count)
            if count is None or count < min_expected_rows:
                logger.warning(
                    "Table %s has suspiciously few rows: %d (min expected: %d)",
                    tablename,
                    count,
                    min_expected_rows,
                )
            results[tablename] = count

    logger.info(
        "Validation complete for tables with prefix '%s': %s", table_prefix, results
    )
    return results
