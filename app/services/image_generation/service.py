# app/services/image_generation/service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from uuid import uuid4
from datetime import datetime

from app.db.models.poi_enhancements import POIImage
from app.db.models.generation_jobs.image_generation_job import ImageGenerationJob
from app.db.enums import GenerationJobStatus, ImageResolution, EnhancementStatus
from app.services.generation.prompt_builder import PromptBuilder
from app.db.queries.prompt_templates import get_image_prompt_template
from app.db.queries.poi import get_poi_by_id
from app.db.queries.poi_enhancements.poi_images import get_style_id as get_image_style_id, get_aspect_id
from app.exceptions.db import NotFoundInDBError
from app.tasks.image_generation import generate_image_task  # celery task

class ImageGenerationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_generate_image(
        self,
        *,
        poi_id: int,
        style_name: str,
        aspect_name: str = "default",
        resolution: ImageResolution = ImageResolution.medium,
        provider: str = "dalle",
        model: str = "dall-e-3",
        force: bool = False,
        prompt_version: int = 1,
    ):
        poi = await get_poi_by_id(self.session, poi_id)
        if not poi:
            raise NotFoundInDBError(f"POI with id {poi_id} not found")
        
        # ---- Resolve style and aspect names to IDs here ----
        style_id = await get_image_style_id(self.session, style_name)
        aspect_id = await get_aspect_id(self.session, aspect_name) if aspect_name else None

        context_data = {
            "name": poi["name"],
            "lat": poi["lat"],
            "lon": poi["lon"],
            "description": poi["description"],
        }

        # 1. DB lookup for existing image
        stmt = select(POIImage).where(
            POIImage.poi_id == poi_id,
            POIImage.style_id == style_id,
            POIImage.aspect_id == aspect_id,
            POIImage.resolution == resolution,
        )
        result = await self.session.execute(stmt)
        image_row = result.scalars().first()

        if image_row is not None and not force:
            # SSOT: If task_id is NULL and status is active, it's a manual/curated asset and always "ready"
            if not image_row.task_id and image_row.status == EnhancementStatus.active:
                return {
                    "status": "ready",
                    "poi_id": image_row.poi_id,
                    "image": image_row,
                }
            # If task_id is set, look up the job row for status
            else:
                job_stmt = select(ImageGenerationJob).where(ImageGenerationJob.task_id == image_row.task_id)
                job_result = await self.session.execute(job_stmt)
                job_row = job_result.scalars().first()
                if job_row:
                    return {
                        "status": job_row.status,
                        "task_id": job_row.task_id,
                        "poi_id": image_row.poi_id,
                        "image": image_row
                    }
                # Fallback: If job row is missing, treat as generating (or handle as error)
                return {
                    "status": "generating",
                    "task_id": image_row.task_id,
                    "poi_id": image_row.poi_id,
                    "image": image_row
                }

        # 2. Compose prompt
        tmpl = await get_image_prompt_template(
            self.session, provider, model, style_id, aspect_id, prompt_version
        )
        if not tmpl:
            raise NotFoundInDBError("Image prompt template not found for these parameters")
        builder = PromptBuilder(tmpl.template)
        prompt = builder.render(**(context_data or {}))

        task_id = str(uuid4())
        now = datetime.utcnow()

        job = ImageGenerationJob(
            task_id=task_id,
            poi_id=poi_id,
            payload={
                "poi_id": poi_id,
                "style_id": style_id,
                "aspect_id": aspect_id,
                "resolution": resolution,
                "provider": provider,
                "model": model,
                "prompt": prompt,
                "context_data": context_data,
            },
            status=GenerationJobStatus.generating,
            created_at=now,
        )
        self.session.add(job)
        await self.session.commit()

        # 4. Insert or update image row
        if image_row is not None:
            upd = (
                update(POIImage)
                .where(POIImage.id == image_row.id)
                .values(
                    prompt=prompt,
                    task_id=task_id,
                    updated_at=now,
                )
            )
            await self.session.execute(upd)
        else:
            ins = insert(POIImage).values(
                poi_id=poi_id,
                style_id=style_id,
                aspect_id=aspect_id,
                resolution=resolution,
                prompt=prompt,
                status=EnhancementStatus.active,
                task_id=task_id,
                created_at=now,
                updated_at=now,
            )
            await self.session.execute(ins)
        await self.session.commit()


        # Dispatch Celery task
        generate_image_task.delay(
            poi_id=poi_id,
            style_id=style_id,
            aspect_id=aspect_id,
            resolution=resolution,
            provider=provider,
            model=model,
            prompt=prompt,
            task_id=task_id,
            context_data=context_data or {},
        )

        return {"status": "generating", "task_id": task_id, "poi_id": poi_id}
