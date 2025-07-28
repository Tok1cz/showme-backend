from celery import shared_task
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import SyncSessionLocal
from app.db.models.poi_enhancements import POIAudio
from app.db.models.generation_jobs.audio_generation_job import AudioGenerationJob
from app.services.generation.registry import registry
from app.db.enums import GenerationJobStatus
from app.services.media_storage import MediaStorage

@shared_task
def generate_audio_task(
    poi_id,
    style_id,
    quality,
    length,
    provider,
    model,
    voice_id,
    prompt,
    task_id,
    context_data,
):
    with SyncSessionLocal() as session:
        try:
            job = session.query(AudioGenerationJob).filter_by(task_id=task_id).first()
            if job:
                job.status = GenerationJobStatus.GENERATING # type: ignore
                session.commit()
            provider_instance = registry.get_audio(provider)

            # Call async provider if needed
            if hasattr(provider_instance.generate, "__call__") and asyncio.iscoroutinefunction(provider_instance.generate):
                audio_bytes = asyncio.run(provider_instance.generate(prompt, model=model, voice=voice_id, **(context_data or {})))
            else:
                audio_bytes = provider_instance.generate(prompt, model=model, voice=voice_id, **(context_data or {}))

            # Save audio bytes using MediaStorage
            audio_filename = f"audio_{task_id}.mp3"
            audio_url = MediaStorage.save_audio(audio_filename, audio_bytes)

            session.query(POIAudio).filter(
                POIAudio.poi_id == poi_id,
                POIAudio.style_id == style_id,
                POIAudio.quality == quality,
                POIAudio.length == length,
                POIAudio.task_id == task_id
            ).update({
                "audio_url": audio_url,
                "filename": audio_filename,
                "status": GenerationJobStatus.ready,
                "error_msg": None,
                "updated_at": datetime.utcnow(),
            })

            if job:
                job.status = GenerationJobStatus.ready # type: ignore
                job.result = {"audio_url": audio_url} # type: ignore
                job.error_msg = None # type: ignore
                job.finished_at = datetime.utcnow() # type: ignore
            session.commit()
        except Exception as e:
            print(e)
            session.query(POIAudio).filter(
                POIAudio.poi_id == poi_id,
                POIAudio.style_id == style_id,
                POIAudio.quality == quality,
                POIAudio.length == length,
                POIAudio.task_id == task_id
            ).update({
                "status": GenerationJobStatus.failed,
                "error_msg": str(e),
                "updated_at": datetime.utcnow(),
            })
            job = session.query(AudioGenerationJob).filter_by(task_id=task_id).first()
            if job:
                job.status = GenerationJobStatus.failed # type: ignore
                job.error_msg = str(e) if e else None # type: ignore
                job.finished_at = datetime.utcnow() # type: ignore
            session.commit()
