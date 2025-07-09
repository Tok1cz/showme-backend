import logging
from sqlalchemy import create_engine, text
from datetime import datetime

from app.core.settings import settings

logger = logging.getLogger(__name__)

class OSMSwapError(Exception):
    pass

def swap_osm_tables(
    db_url: str = None,
    live_prefix: str = "planet_osm",
    new_prefix: str = "planet_osm_new",
    table_types = ("point", "line", "polygon", "nodes", "rels", "ways"),
    archive: bool = True
) -> None:
    """
    Atomically swaps the temp OSM tables in as the new live tables.
    Optionally archives old tables with a timestamp suffix.
    """
    db_url = db_url or settings.DATABASE_URL_SYNCH
    engine = create_engine(db_url)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    with engine.begin() as conn:  # Transactional
        for t in table_types:
            live_name = f"{live_prefix}_{t}"
            new_name = f"{new_prefix}_{t}"
            archived_name = f"{live_name}_old_{timestamp}"

            # Archive or drop current live table
            exists = conn.execute(
                text("SELECT to_regclass(:tn) IS NOT NULL"), {"tn": live_name}
            ).scalar()
            if exists:
                if archive:
                    logger.info("Archiving live table: %s -> %s", live_name, archived_name)
                    conn.execute(text(f'ALTER TABLE {live_name} RENAME TO {archived_name}'))
                else:
                    logger.info("Dropping live table: %s", live_name)
                    conn.execute(text(f'DROP TABLE {live_name}'))

            # Rename new table to live
            logger.info("Promoting %s -> %s", new_name, live_name)
            conn.execute(text(f'ALTER TABLE {new_name} RENAME TO {live_name}'))

    logger.info("Blue-green OSM table swap complete. Live tables updated.")
