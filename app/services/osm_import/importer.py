import logging
import os
import subprocess
from pathlib import Path

from app.core.settings import settings

logger = logging.getLogger(__name__)

class OSMImportError(Exception):
    pass

def import_osm_to_temp_tables(
    merged_file: Path,
    db_url: str = None,
    table_prefix: str = "planet_osm_new"
) -> None:
    """
    Imports the merged OSM file into Postgres temp tables using osm2pgsql.
    Creates tables with a unique prefix (e.g. planet_osm_new_point, ...).
    """
    if not merged_file.exists():
        logger.error("Merged OSM file not found: %s", merged_file)
        raise OSMImportError(f"Merged OSM file not found: {merged_file}")

    # Parse DB connection info from settings (or override)
    # Assumes DB URL is like: postgres://user:password@host:port/dbname
    from urllib.parse import urlparse
    db_url = db_url or settings.DATABASE_URL_SYNCH
    parsed = urlparse(db_url)

    dbname = parsed.path.lstrip('/')
    dbuser = parsed.username
    dbhost = parsed.hostname
    dbport = parsed.port or 5432
    dbpassword = parsed.password


    cmd = [
        "osm2pgsql",
        "--create",
        "--slim",
        "--database", dbname,
        "-U", dbuser,  # -U is correct!
        "--host", dbhost,
        "--port", str(dbport),
        "--prefix", table_prefix,
        "--hstore",
        str(merged_file),
    ]
    env = os.environ.copy()
    if dbpassword:
        env["PGPASSWORD"] = dbpassword

    # Prompt for password only if needed (or use .pgpass for CI/prod)
    logger.info("Importing merged OSM file into temp tables with prefix '%s'", table_prefix)
    logger.debug("Running command: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd, capture_output=True, check=True, text=True, env=env)
        logger.info("osm2pgsql import completed: %s", result.stdout.strip())
    except subprocess.CalledProcessError as e:
        logger.error("osm2pgsql failed: %s\n%s", e, e.stderr)
        print(e.stdout)
        raise OSMImportError(f"osm2pgsql failed: {e.stderr}")

    logger.info("Temp tables created with prefix '%s'.", table_prefix)
