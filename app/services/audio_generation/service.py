# app/services/audio_generation/service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from uuid import uuid4
from datetime import datetime

from app.db.models.poi_enhancements import POIAudio
from app.db.models.generation_jobs.audio_generation_job import AudioGenerationJob
from app.db.enums import GenerationJobStatus, AudioQuality, AudioLength, EnhancementStatus
from app.services.generation.prompt_builder import PromptBuilder
from app.services.generation.registry import registry
from app.db.queries.prompt_templates import get_audio_prompt_template
from app.db.queries.poi import get_poi_by_id
from app.db.queries.poi_audio import get_style_id as get_audio_style_id
from app.exceptions.db import NotFoundInDBError
from app.tasks.audio_generation import generate_audio_task  # celery task

class AudioGenerationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_generate_audio(
        self,
        *,
        poi_id: int,
        style_id: int,
        quality: AudioQuality = AudioQuality.MEDIUM,
        length: AudioLength = AudioLength.MEDIUM,
        provider: str = "bark",
        model: str = "bark-large",
        voice_id: int = None,
        force: bool = False,
        prompt_version: int = 1,
    ):
        poi = await get_poi_by_id(self.session, poi_id)
        if not poi:
            raise NotFoundInDBError(f"POI with id {poi_id} not found")
        
        context_data = {
            "name": poi["name"],
            "lat": poi["lat"],
            "lon": poi["lon"],
            "description": poi["description"],
        }

        # 1. DB lookup for existing audio
        stmt = select(POIAudio).where(
            POIAudio.poi_id == poi_id,
            POIAudio.style_id == style_id,
            POIAudio.quality == quality,
            POIAudio.length == length,
        )
        result = await self.session.execute(stmt)
        audio_row = result.scalars().first()

        if audio_row is not None and not force:
            if audio_row.status == EnhancementStatus.ACTIVE:
                return audio_row
            elif audio_row.status == GenerationJobStatus.GENERATING:
                return {"status": "generating", "task_id": audio_row.task_id}

        tmpl = await get_audio_prompt_template(
            self.session, provider, model, voice_id, prompt_version
        )
        if not tmpl:
            raise NotFoundInDBError("Audio prompt template not found for these parameters")
        builder = PromptBuilder(tmpl.template)
        prompt = builder.render(**(context_data or {}))

        task_id = str(uuid4())
        now = datetime.utcnow()

        # 4. Insert or update audio row
        if audio_row is not None:
            upd = (
                update(POIAudio)
                .where(POIAudio.id == audio_row.id)
                .values(
                    status=GenerationJobStatus.GENERATING,
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    prompt_version=tmpl.version,
                    task_id=task_id,
                    error_msg=None,
                    updated_at=now,
                )
            )
            await self.session.execute(upd)
        else:
            ins = insert(POIAudio).values(
                poi_id=poi_id,
                style_id=style_id,
                quality=quality,
                length=length,
                prompt=prompt,
                provider=provider,
                model=model,
                prompt_version=tmpl.version,
                status=GenerationJobStatus.GENERATING,
                task_id=task_id,
                created_at=now,
                updated_at=now,
            )
            await self.session.execute(ins)

        job = AudioGenerationJob(
            task_id=task_id,
            payload={
                "poi_id": poi_id,
                "style_id": style_id,
                "quality": quality,
                "length": length,
                "provider": provider,
                "model": model,
                "voice_id": voice_id,
                "prompt": prompt,
                "context_data": context_data,
            },
            status=GenerationJobStatus.GENERATING,
            created_at=now,
        )
        self.session.add(job)
        await self.session.commit()

        # Dispatch Celery task
        generate_audio_task.delay(
            poi_id=poi_id,
            style_id=style_id,
            quality=quality,
            length=length,
            provider=provider,
            model=model,
            voice_id=voice_id,
            prompt=prompt,
            task_id=task_id,
            context_data=context_data or {},
        )

        return {"status": "generating", "task_id": task_id}
