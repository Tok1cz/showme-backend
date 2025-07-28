from celery import shared_task
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import SyncSessionLocal
from app.db.models.poi_enhancements import POIImage
from app.db.models.generation_jobs.image_generation_job import ImageGenerationJob
from app.services.generation.registry import registry
from app.db.enums import GenerationJobStatus
from app.services.media_storage import MediaStorage
from app.core import settings
import requests  # For downloading image data from URL, if needed

@shared_task
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
                job.status = GenerationJobStatus.generating # type: ignore
                session.commit()
            provider_instance = registry.get_image(provider)

            # Call async provider if needed
            if hasattr(provider_instance.generate, "__call__") and asyncio.iscoroutinefunction(provider_instance.generate):
                result = asyncio.run(provider_instance.generate(prompt, model=model, **(context_data or {})))
            else:
                result = provider_instance.generate(prompt, model=model, **(context_data or {}))

            # Assume result is a list of image dicts with .url (OpenAI pattern)
            image_url = result[0].url if isinstance(result, list) and hasattr(result[0], "url") else result[0]["url"] if isinstance(result, list) else result.get("url")
            image_filename = f"image_{task_id}.png"

            # If using CDN/local, download image bytes and store via MediaStorage
            if image_url and (MediaStorage.save_image != "local" or settings.MEDIA_STORAGE_BACKEND == "cdn"):
                image_data = requests.get(image_url).content
                stored_url = MediaStorage.save_image(image_filename, image_data)
            else:
                stored_url = image_url

            session.query(POIImage).filter(
                POIImage.poi_id == poi_id,
                POIImage.style_id == style_id,
                POIImage.aspect_id == aspect_id,
                POIImage.resolution == resolution,
                POIImage.task_id == task_id # Well we need to update the data model again .. 
            ).update({
                "image_url": stored_url,
                "filename": image_filename,
                "status": GenerationJobStatus.ready,
                "error_msg": None,
                "updated_at": datetime.utcnow(),
            })

            if job:
                job.status = GenerationJobStatus.ready 
                job.result = {"image_url": stored_url} # type: ignore
                job.error_msg = None # type: ignore
                job.finished_at = datetime.utcnow() # type: ignore
            session.commit()
        except Exception as e:
            print(e)
            session.query(POIImage).filter(
                POIImage.poi_id == poi_id,
                POIImage.style_id == style_id,
                POIImage.aspect_id == aspect_id,
                POIImage.resolution == resolution,
                POIImage.task_id == task_id
            ).update({
                "status": GenerationJobStatus.failed,
                "error_msg": str(e),
                "updated_at": datetime.utcnow(),
            })
            job = session.query(ImageGenerationJob).filter_by(task_id=task_id).first()
            if job:
                job.status = GenerationJobStatus.failed # type: ignore
                job.error_msg = str(e) if e else None # type: ignore
                job.finished_at = datetime.utcnow() # type: ignore
            session.commit()
