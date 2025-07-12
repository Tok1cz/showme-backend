import logging
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta, timezone

from app.core.settings import settings

logger = logging.getLogger(__name__)

from datetime import datetime, timedelta


def cleanup_old_osm_tables(
    db_url: str = None,
    live_prefix: str = "planet_osm",
    table_types=("point", "line", "polygon", "nodes", "rels", "ways"),
    retention_days: int = None,
):
    """
    Drops archived/old OSM tables whose timestamp suffix is older than retention period,
    or (if retention_days < 0) drops all old tables regardless of timestamp.
    """
    db_url = db_url or settings.DATABASE_URL_SYNCH
    retention_days = (
        retention_days if retention_days is not None else settings.OSM_RETENTION_DAYS
    )
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=abs(retention_days))
    logger.info(f"Now: {now}, Retention_days: {retention_days}, Cutoff: {cutoff}")

    engine = create_engine(db_url)
    with engine.begin() as conn:
        for t in table_types:
            regex = f"^{live_prefix}_{t}_old_\\d{{14}}$"
            result = conn.execute(
                text("SELECT tablename FROM pg_tables WHERE tablename ~ :regex"),
                {"regex": regex},
            )
            to_drop = []
            for (tablename,) in result:
                if retention_days < 0:
                    # Drop all matching tables
                    to_drop.append(tablename)
                else:
                    ts_str = tablename.rsplit("_old_", 1)[-1]
                    try:
                        table_dt = datetime.strptime(ts_str, "%Y%m%d%H%M%S").replace(
                            tzinfo=timezone.utc
                        )
                        if retention_days == 0:
                            if table_dt < now:
                                to_drop.append(tablename)
                        else:  # retention_days > 0
                            if table_dt < cutoff:
                                to_drop.append(tablename)
                    except Exception as e:
                        logger.warning(
                            f"Failed parsing timestamp for table '{tablename}': {e}"
                        )
            logger.info(f"Tables to drop for '{t}': {to_drop}")
            for tablename in to_drop:
                logger.info(f"Dropping table: {tablename}")
                conn.execute(text(f"DROP TABLE IF EXISTS {tablename}"))


import os
from pathlib import Path


def cleanup_old_files(import_dir: str = None, retention_days: int = None):
    """
    Deletes OSM files in the import dir older/newer than retention period,
    following positive/zero/negative retention logic.
    """
    import_dir = Path(import_dir or settings.OSM_IMPORT_DIR)
    retention_days = (
        retention_days if retention_days is not None else settings.OSM_RETENTION_DAYS
    )
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=retention_days)

    for f in import_dir.glob("*.osm.pbf"):
        # Always get mtime in UTC
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)

        # Positive: drop if mtime < cutoff
        # Zero:     drop if mtime < now
        # Negative: drop if mtime > now (future file)
        should_delete = (
            (retention_days > 0 and mtime < cutoff)
            or (retention_days == 0 and mtime < now)
            or (retention_days < 0 and mtime > now)
        )
        if should_delete:
            try:
                f.unlink()
                logger.info("Deleted old file: %s", f)
            except Exception as e:
                logger.warning("Failed to delete old file: %s (%s)", f, e)
