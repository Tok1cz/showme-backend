import logging
import requests
from pathlib import Path
from typing import List, Dict

from app.core.settings import settings

logger = logging.getLogger(__name__)

class OSMDownloadError(Exception):
    pass

def ensure_import_dir() -> Path:
    """Ensure the OSM import directory exists (cross-platform, idempotent)."""
    import_dir = Path(settings.OSM_IMPORT_DIR)
    if not import_dir.exists():
        logger.info("Creating OSM import dir: %s", import_dir)
        import_dir.mkdir(parents=True, exist_ok=True)
    return import_dir

def build_download_url(region: str) -> str:
    """Builds the OSM download URL for the given region."""
    return "%s%s/%s-latest.osm.pbf" % (settings.OSM_BASE_URL, settings.CONTINENT, region)

def download_file(url: str, dest_path: Path, chunk_size: int = 8192) -> None:
    """Streams a file from url to dest_path. Raises OSMDownloadError on fail."""
    try:
        with requests.get(url, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
        logger.info("Downloaded %s to %s", url, dest_path)
    except Exception as e:
        logger.error("Download failed for %s: %s", url, e)
        raise OSMDownloadError("Failed to download %s: %s" % (url, e))

def fetch_osm_files(regions: List[str] = None) -> Dict[str, Path]:
    """
    Downloads .osm.pbf files for all specified regions (default: settings.REGIONS).
    Returns a dict: region -> Path to downloaded file.
    """
    import_dir = ensure_import_dir()
    results = {}

    region_list = regions if regions is not None else settings.REGIONS
    for region in region_list:
        url = build_download_url(region)
        filename = "%s-latest.osm.pbf" % region
        dest_path = import_dir / filename
        if dest_path.exists() and dest_path.stat().st_size > 0:
            logger.info("File already exists, skipping download: %s", dest_path)
            results[region] = dest_path
            continue
        logger.info("Fetching %s: %s", region, url)
        download_file(url, dest_path)
        results[region] = dest_path

    return results
