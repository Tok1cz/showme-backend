import logging

from sqlalchemy import create_engine, text

from app.core.settings import settings

logger = logging.getLogger(__name__)


def preimport_cleanup(db_url: str = None, temp_prefix: str = "planet_osm_new"):
    """
    Drops any leftover tables, constraints, functions, triggers, and indexes with the given temp prefix.
    Prevents blocking on new OSM imports after failed/interrupted swaps.
    """
    db_url = db_url or settings.DATABASE_URL_SYNCH
    engine = create_engine(db_url)
    with engine.begin() as conn:
        # 1. Drop tables (CASCADE to remove related triggers/functions/etc.)
        tables = conn.execute(
            text(
                """
            SELECT tablename FROM pg_tables
            WHERE tablename LIKE :prefix
        """
            ),
            {"prefix": f"{temp_prefix}%"},
        )
        for (tablename,) in tables:
            logger.info("Dropping leftover table: %s", tablename)
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {tablename} CASCADE"))
            except Exception as e:
                logger.warning("Failed to drop table %s: %s", tablename, e)

        # 2. Drop constraints (Primary Key, Unique, etc.)
        constraints = conn.execute(
            text(
                """
            SELECT conname, conrelid::regclass::text AS tablename
            FROM pg_constraint
            WHERE conname LIKE :prefix
        """
            ),
            {"prefix": f"{temp_prefix}%"},
        )
        for conname, tablename in constraints:
            logger.info("Dropping constraint: %s on table %s", conname, tablename)
            try:
                conn.execute(
                    text(
                        f"ALTER TABLE {tablename} DROP CONSTRAINT IF EXISTS {conname} CASCADE"
                    )
                )
            except Exception as e:
                logger.warning(
                    "Failed to drop constraint %s on %s: %s", conname, tablename, e
                )

        # 3. Drop functions with the prefix
        functions = conn.execute(
            text(
                """
            SELECT proname, oidvectortypes(proargtypes) as argtypes
            FROM pg_proc
            WHERE proname LIKE :prefix
        """
            ),
            {"prefix": f"{temp_prefix}%"},
        )
        for fname, argtypes in functions:
            logger.info("Dropping leftover function: %s(%s)", fname, argtypes)
            try:
                # Handles functions with and without arguments
                conn.execute(
                    text(f"DROP FUNCTION IF EXISTS {fname}({argtypes}) CASCADE")
                )
            except Exception as e:
                logger.warning("Failed to drop function %s(%s): %s", fname, argtypes, e)

        # 4. Drop triggers with the prefix
        triggers = conn.execute(
            text(
                """
            SELECT tgname, relname
            FROM pg_trigger
            JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
            WHERE tgname LIKE :prefix
        """
            ),
            {"prefix": f"{temp_prefix}%"},
        )
        for tname, relname in triggers:
            logger.info("Dropping leftover trigger: %s ON %s", tname, relname)
            try:
                conn.execute(
                    text(f"ALTER TABLE {relname} DROP TRIGGER IF EXISTS {tname}")
                )
            except Exception as e:
                logger.warning("Failed to drop trigger %s on %s: %s", tname, relname, e)

        # 5. Drop indexes with the prefix (after constraints!)
        indexes = conn.execute(
            text(
                """
            SELECT indexname FROM pg_indexes
            WHERE indexname LIKE :prefix
        """
            ),
            {"prefix": f"{temp_prefix}%"},
        )
        for (idxname,) in indexes:
            logger.info("Dropping leftover index: %s", idxname)
            try:
                conn.execute(text(f"DROP INDEX IF EXISTS {idxname} CASCADE"))
            except Exception as e:
                logger.warning("Failed to drop index %s: %s", idxname, e)
