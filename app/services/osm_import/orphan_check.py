import logging

from sqlalchemy import create_engine, text

from app.core.settings import settings

logger = logging.getLogger(__name__)

ENRICHMENT_TABLES = [
    {"table": "poi_info_texts", "poi_id_col": "poi_id", "geom_col": "geometry_type"},
    {"table": "poi_images", "poi_id_col": "poi_id", "geom_col": "geometry_type"},
    # Add future enrichment tables here, e.g.:
    # {"table": "poi_audiofiles", "poi_id_col": "poi_id", "geom_col": "geometry_type"},
]

PLANET_OSM_TABLES = {
    "POINT": "planet_osm_point",
    "LINESTRING": "planet_osm_line",
    "POLYGON": "planet_osm_polygon",
    "MULTIPOLYGON": "planet_osm_polygon",
    "MULTILINESTRING": "planet_osm_line",
}


def update_orphan_flags(db_url: str = None):
    """
    After table swap, flag orphans in all enrichment tables.
    An orphan = enrichment.poi_id/geometry_type is not present in live OSM tables.
    """
    db_url = db_url or settings.DATABASE_URL_SYNCH
    engine = create_engine(db_url)
    with engine.begin() as conn:
        for entry in ENRICHMENT_TABLES:
            tab = entry["table"]
            poi_col = entry["poi_id_col"]
            geom_col = entry["geom_col"]
            total = 0
            orphans = 0
            unorphans = 0

            # Count all
            res = conn.execute(text(f"SELECT COUNT(*) FROM {tab}"))
            total = res.scalar()
            logger.info("Checking enrichment table: %s (%d rows)", tab, total)

            # Set orphan = TRUE if referenced OSM object does NOT exist
            # Only update those not already orphaned
            for geom_type, planet_table in PLANET_OSM_TABLES.items():
                upd = conn.execute(
                    text(
                        f"""
                    UPDATE {tab}
                    SET orphan = TRUE
                    WHERE {geom_col} = :geom_type
                      AND orphan IS DISTINCT FROM TRUE
                      AND NOT EXISTS (
                        SELECT 1 FROM {planet_table}
                        WHERE {planet_table}.osm_id = {tab}.{poi_col}
                      )
                """
                    ),
                    {"geom_type": geom_type},
                )
                orphans += upd.rowcount or 0
                logger.info(
                    "Orphaned %d rows in %s for %s", upd.rowcount or 0, tab, geom_type
                )

            # Set orphan = FALSE if referenced OSM object now exists again (record was previously orphaned)
            for geom_type, planet_table in PLANET_OSM_TABLES.items():
                upd = conn.execute(
                    text(
                        f"""
                    UPDATE {tab}
                    SET orphan = FALSE
                    WHERE {geom_col} = :geom_type
                      AND orphan IS DISTINCT FROM FALSE
                      AND EXISTS (
                        SELECT 1 FROM {planet_table}
                        WHERE {planet_table}.osm_id = {tab}.{poi_col}
                      )
                """
                    ),
                    {"geom_type": geom_type},
                )
                unorphans += upd.rowcount or 0
                logger.info(
                    "Un-orphaned %d rows in %s for %s",
                    upd.rowcount or 0,
                    tab,
                    geom_type,
                )

            logger.info(
                "Orphan check complete for %s: %d orphaned, %d un-orphaned, %d total",
                tab,
                orphans,
                unorphans,
                total,
            )
