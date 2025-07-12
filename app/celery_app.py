from celery import Celery
from app.core.settings import settings
from app.services.generation.providers import register_providers

celery_app = Celery(
    "osm_import",
    broker=settings.CELERY_BROKER_URL,  # e.g., "redis://localhost:6379/0"
    backend=settings.CELERY_BACKEND_URL,  # optional: "redis://localhost:6379/1"
    include=["app.services.osm_import.runner"],
)
celery_app.autodiscover_tasks([
    "app.tasks",
])
register_providers()
import app.tasks.text_generation