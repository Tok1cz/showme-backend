import logging
import shutil
import traceback
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.celery_app import celery_app
from app.core.settings import settings
from app.db.models.log_models import OSMImportLog, OSMImportStatus
from app.services.osm_import.cleanup import cleanup_old_files, cleanup_old_osm_tables
from app.services.osm_import.downloader import fetch_osm_files
from app.services.osm_import.filter import filter_osm_files
from app.services.osm_import.importer import import_osm_to_temp_tables
from app.services.osm_import.merge import merge_osm_files
from app.services.osm_import.orphan_check import update_orphan_flags
from app.services.osm_import.preimport_cleanup import preimport_cleanup
from app.services.osm_import.swapper import swap_osm_tables
from app.services.osm_import.vacuum import vacuum_analyze_osm_tables
from app.services.osm_import.validator import validate_imported_tables

logger = logging.getLogger(__name__)


def wipe_import_dir(import_dir: str = None):
    """
    Removes all .osm.pbf files from the import directory before starting a new import.
    """
    import_dir = Path(import_dir or settings.OSM_IMPORT_DIR)
    if import_dir.exists():
        for f in import_dir.glob("*.osm.pbf"):
            try:
                f.unlink()
            except Exception as e:
                logger.warning("Failed to remove file %s: %s", f, e)


def run_osm_import(task_id=None):
    """
    Orchestrates the full OSM import pipeline. Logs to OSMImportLog.
    Returns: dict with status/result.
    """
    # Setup DB session for logging
    engine = create_engine(settings.DATABASE_URL_SYNCH)
    Session = sessionmaker(bind=engine)
    db = Session()

    log = OSMImportLog(
        started_at=datetime.utcnow(),
        status="started",
        regions=settings.REGIONS,
        files=None,
        record_count=None,
        error=None,
        notes="Import started.",
        task_id=task_id,  # store the Celery task id
    )
    db.add(log)
    db.commit()  # log.id available

    try:
        # -1. Clean up any leftovers from previous temp tables/functions/etc.
        preimport_cleanup()
        # 0. Wipe tmp folder
        wipe_import_dir()
        # 1. Download
        raw_files = fetch_osm_files()
        log.files = {r: str(f) for r, f in raw_files.items()}
        db.commit()

        # 2. Filter
        filtered_files = filter_osm_files(raw_files)

        # 3. Merge
        merged_file = merge_osm_files(filtered_files)

        # 4. Import to temp tables
        import_osm_to_temp_tables(merged_file)

        # 5. Validate
        stats = validate_imported_tables()
        log.record_count = sum(stats.values())
        db.commit()

        # 6. Swap tables
        swap_osm_tables()

        cleanup_old_osm_tables()
        cleanup_old_files()

        # Success!
        log.finished_at = datetime.utcnow()
        log.status = OSMImportStatus.completed
        log.notes = f"Import successful. Row counts: {stats}"
        db.commit()
        logger.info("OSM import pipeline completed successfully.")

        return {"status": "completed", "import_log_id": log.id, "stats": stats}
    except Exception as e:
        tb = traceback.format_exc()
        log.finished_at = datetime.utcnow()
        log.status = OSMImportStatus.failed
        log.error = f"{e}\n{tb}"
        log.notes = "Import failed."
        db.commit()
        logger.error("OSM import failed: %s\n%s", e, tb)
        return {
            "status": "failed",
            "import_log_id": log.id,
            "error": str(e),
            "traceback": tb,
        }
    finally:
        db.close()


@celery_app.task(bind=True)
def run_osm_import_task(self):
    # Optionally pass the celery task ID for logging
    return run_osm_import(task_id=self.request.id)
