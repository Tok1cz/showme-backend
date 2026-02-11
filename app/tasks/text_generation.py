from celery import shared_task
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import SyncSessionLocal
from app.db.models.poi_enhancements import POIInfoText
from app.db.models.generation_jobs.text_generation_job import TextGenerationJob
from app.services.generation.registry import registry
from app.db.enums import GenerationJobStatus
from app.db.enums import EnhancementStatus
import logging

logger = logging.getLogger(__name__)


@shared_task(rate_limit="5/m")
def generate_info_text_task(
    poi_id,
    topic_id,
    style_id,
    text_length,
    provider,
    model,
    prompt,
    task_id,
    context_data,
):
    with SyncSessionLocal() as session:
        try:
            job = session.query(TextGenerationJob).filter_by(task_id=task_id).first()
            if job:
                job.status = GenerationJobStatus.generating  # type: ignore
                session.commit()
            provider_instance = registry.get_text(provider)

            if hasattr(
                provider_instance.generate, "__call__"
            ) and asyncio.iscoroutinefunction(provider_instance.generate):
                info_text = asyncio.run(
                    provider_instance.generate(
                        prompt, model=model, **(context_data or {})
                    )
                )
            else:
                info_text = provider_instance.generate(
                    prompt, model=model, **(context_data or {})
                )
            # Update POIInfoText
            session.query(POIInfoText).filter(
                POIInfoText.poi_id == poi_id,
                POIInfoText.topic_id == topic_id,
                POIInfoText.style_id == style_id,
                POIInfoText.text_length == text_length,
                POIInfoText.task_id == task_id,
            ).update(
                {
                    "info_text": info_text,
                    "status": EnhancementStatus.active,
                    "updated_at": datetime.utcnow(),
                }
            )
            if job:
                job.status = GenerationJobStatus.ready  # type: ignore
                job.result = {"info_text": info_text}  # type: ignore
                job.error_msg = None  # type: ignore
                job.finished_at = datetime.utcnow()  # type: ignore
            session.commit()
        except Exception as e:
            logger.warning("Exception in %s: %s", __name__, e, exc_info=True)
            session.query(POIInfoText).filter(
                POIInfoText.poi_id == poi_id,
                POIInfoText.topic_id == topic_id,
                POIInfoText.style_id == style_id,
                POIInfoText.text_length == text_length,
                POIInfoText.task_id == task_id,
            ).update(
                {
                    "status": EnhancementStatus.inactive,
                    "updated_at": datetime.utcnow(),
                }
            )
            job = session.query(TextGenerationJob).filter_by(task_id=task_id).first()
            if job:
                job.status = GenerationJobStatus.failed  # type: ignore
                job.error_msg = str(e) if e else None  # type: ignore
                job.finished_at = datetime.utcnow()  # type: ignore
            session.commit()
