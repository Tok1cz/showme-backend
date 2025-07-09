from celery import Celery
from app.core.settings import settings

celery_app = Celery(
    "osm_import",
    broker=settings.CELERY_BROKER_URL,  # e.g., "redis://localhost:6379/0"
    backend=settings.CELERY_BACKEND_URL,  # optional: "redis://localhost:6379/1"
    include=["app.services.osm_import.runner"],
)
