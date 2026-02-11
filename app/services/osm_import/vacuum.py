import logging

from sqlalchemy import create_engine, text

from app.core.settings import settings

logger = logging.getLogger(__name__)


def vacuum_analyze_osm_tables(
    db_url: str = None,
    table_prefix: str = "planet_osm",
    table_types=("point", "line", "polygon"),
):
    """
    Runs VACUUM ANALYZE on all OSM data tables after a swap/import.
    """
    db_url = db_url or settings.DATABASE_URL_SYNCH
    engine = create_engine(db_url)
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for t in table_types:
            tablename = f"{table_prefix}_{t}"
            logger.info("Running VACUUM ANALYZE on %s", tablename)
            conn.execute(text(f"VACUUM ANALYZE {tablename}"))
    logger.info("VACUUM ANALYZE complete on all OSM tables.")
