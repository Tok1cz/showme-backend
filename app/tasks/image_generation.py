from celery import shared_task
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import SyncSessionLocal
from app.db.models.poi_enhancements import POIImage
from app.db.models.generation_jobs.image_generation_job import ImageGenerationJob
from app.services.generation.registry import registry
from app.db.enums import GenerationJobStatus
from app.db.enums import EnhancementStatus
from app.services.media_storage import MediaStorage
from app.core.settings import settings
import requests  # For downloading image data from URL, if needed
import logging

logger = logging.getLogger(__name__)


@shared_task(rate_limit="5/m")
def generate_image_task(
    poi_id,
    style_id,
    aspect_id,
    resolution,
    provider,
    model,
    prompt,
    task_id,
    context_data,
):
    with SyncSessionLocal() as session:
        try:
            job = session.query(ImageGenerationJob).filter_by(task_id=task_id).first()
            if job:
                job.status = GenerationJobStatus.generating  # type: ignore
                session.commit()
            provider_instance = registry.get_image(provider)

            if hasattr(
                provider_instance.generate, "__call__"
            ) and asyncio.iscoroutinefunction(provider_instance.generate):
                result = asyncio.run(
                    provider_instance.generate(
                        prompt, model=model, **(context_data or {})
                    )
                )
            else:
                result = provider_instance.generate(
                    prompt, model=model, **(context_data or {})
                )

            image_url = (
                result[0].url
                if isinstance(result, list) and hasattr(result[0], "url")
                else result[0]["url"] if isinstance(result, list) else result.get("url")
            )
            image_filename = f"image_{task_id}.png"

            if image_url:
                image_data = requests.get(image_url).content
                stored_url = MediaStorage.save_image(image_filename, image_data)

            session.query(POIImage).filter(
                POIImage.poi_id == poi_id,
                POIImage.style_id == style_id,
                POIImage.aspect_id == aspect_id,
                POIImage.resolution == resolution,
                POIImage.task_id == task_id,
            ).update(
                {
                    "image_url": stored_url,
                    "filename": image_filename,
                    "updated_at": datetime.utcnow(),
                    "status": EnhancementStatus.active,
                }
            )

            if job:
                job.status = GenerationJobStatus.ready
                job.result = {"image_url": stored_url}  # type: ignore
                job.error_msg = None  # type: ignore
                job.finished_at = datetime.utcnow()  # type: ignore
            session.commit()
        except Exception as e:
            logger.warning("Exception in %s: %s", __name__, e, exc_info=True)
            session.query(POIImage).filter(
                POIImage.poi_id == poi_id,
                POIImage.style_id == style_id,
                POIImage.aspect_id == aspect_id,
                POIImage.resolution == resolution,
                POIImage.task_id == task_id,
            ).update(
                {
                    "updated_at": datetime.utcnow(),
                    "status": EnhancementStatus.inactive,  # set enhancement status to inactive on failure
                }
            )
            job = session.query(ImageGenerationJob).filter_by(task_id=task_id).first()
            if job:
                job.status = GenerationJobStatus.failed  # type: ignore
                job.error_msg = str(e) if e else None  # type: ignore
                job.finished_at = datetime.utcnow()  # type: ignore
            session.commit()
