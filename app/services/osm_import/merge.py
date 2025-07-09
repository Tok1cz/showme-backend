import logging
import subprocess
from pathlib import Path
from typing import Dict

from app.core.settings import settings

logger = logging.getLogger(__name__)

class OSMMergeError(Exception):
    pass

def merge_osm_files(filtered_file_map: Dict[str, Path], merged_filename: str = "merged-latest.osm.pbf") -> Path:
    """
    Merges all filtered .osm.pbf files into a single .osm.pbf for import.
    Deletes filtered input files after merging.
    Returns path to merged file.
    """
    if not filtered_file_map:
        logger.error("No filtered OSM files provided for merge.")
        raise OSMMergeError("No filtered OSM files provided.")

    import_dir = Path(settings.OSM_IMPORT_DIR)
    merged_path = import_dir / merged_filename

    # Prepare list of files to merge
    input_files = [str(p) for p in filtered_file_map.values()]
    logger.info("Merging filtered OSM files: %s", ", ".join(input_files))
    logger.info("Output merged file: %s", merged_path)

    try:
        cmd = ["osmium", "merge", *input_files, "-o", str(merged_path)]
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        logger.info("osmconvert output: %s", result.stdout.strip())
    except subprocess.CalledProcessError as e:
        logger.error("osmconvert failed: %s\n%s", e, e.stderr)
        raise OSMMergeError(f"osmconvert failed: {e.stderr}")

    # On success, delete filtered temp files
    for region, p in filtered_file_map.items():
        try:
            p.unlink()
            logger.info("Deleted filtered file for %s: %s", region, p)
        except Exception as del_err:
            logger.warning("Failed to delete filtered file for %s: %s (%s)", region, p, del_err)

    return merged_path
