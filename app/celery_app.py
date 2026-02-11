from celery import Celery

import app.tasks.audio_generation
import app.tasks.image_generation
import app.tasks.text_generation
from app.core.settings import settings
from app.services.generation.providers import register_providers

celery_app = Celery(
    "osm_import",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL,
    include=["app.services.osm_import.runner"],
)
celery_app.autodiscover_tasks(
    [
        "app.tasks",
    ]
)
register_providers()
