from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from uuid import uuid4
from datetime import datetime

from app.db.models.poi_enhancements import POIInfoText
from app.db.models.generation_jobs.text_generation_job import TextGenerationJob
from app.db.enums import GenerationJobStatus, TextLength
from app.services.generation.prompt_builder import PromptBuilder
from app.services.generation.registry import registry
from app.db.queries.prompt_templates import get_text_prompt_template
from app.tasks.text_generation import generate_info_text_task  # celery task
from app.db.models.prompt_templates import TextPromptTemplate
from app.db.queries.poi import get_poi_by_id
from app.exceptions.db import NotFoundInDBError

class InfoTextService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_generate_info_text(
        self,
        *,
        poi_id: int,
        topic_id: int,
        style_id: int,
        text_length: TextLength = TextLength.medium,
        provider: str = "openai",
        model: str = "gpt-4o",
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
        # 1. DB lookup for existing info_text
        stmt = select(POIInfoText).where(
            POIInfoText.poi_id == poi_id,
            POIInfoText.topic_id == topic_id,
            POIInfoText.style_id == style_id,
            POIInfoText.text_length == text_length,
        )
        result = await self.session.execute(stmt)
        info_text_row = result.scalars().first()

        if info_text_row is not None and not force:
            if info_text_row.status == GenerationJobStatus.ready:
                return info_text_row  
            elif info_text_row.status == GenerationJobStatus.generating:
                return {"status": "generating", "task_id": info_text_row.task_id}

        # 2. Compose prompt
        tmpl: TextPromptTemplate = await get_text_prompt_template(
            self.session, provider, model, topic_id, style_id, prompt_version
        )
        if not tmpl:
            raise NotFoundInDBError("Prompt template not found for these parameters")
        builder = PromptBuilder(
            tmpl.template if isinstance(tmpl.template, str) else tmpl.template.value
        )
        prompt = builder.render(**(context_data or {}))

        # 3. Generate a new task_id
        task_id = str(uuid4())
        now = datetime.utcnow()

        # 4. Insert or update info_text row
        if info_text_row is not None:
            upd = (
                update(POIInfoText)
                .where(POIInfoText.id == info_text_row.id)
                .values(
                    status="generating",
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
            ins = insert(POIInfoText).values(
                poi_id=poi_id,
                topic_id=topic_id,
                style_id=style_id,
                text_length=text_length,
                prompt=prompt,
                provider=provider,
                model=model,
                prompt_version=tmpl.version,
                status=GenerationJobStatus.generating,
                task_id=task_id,
                created_at=now,
                updated_at=now,
            )
            await self.session.execute(ins)

        # 5. Create a job row
        job = TextGenerationJob(
            task_id=task_id,
            payload={
                "poi_id": poi_id,
                "topic_id": topic_id,
                "style_id": style_id,
                "text_length": text_length,
                "provider": provider,
                "model": model,
                "prompt": prompt,
                "context_data": context_data,
            },
            status="generating",
            created_at=now,
        )
        self.session.add(job)
        await self.session.commit()

        # 6. Dispatch Celery task
        generate_info_text_task.delay(
            poi_id=poi_id,
            topic_id=topic_id,
            style_id=style_id,
            text_length=text_length,
            provider=provider,
            model=model,
            prompt=prompt,
            task_id=task_id,
            context_data=context_data or {},
        )

        return {"status": "generating", "task_id": task_id}

    async def bulk_get_or_generate_info_texts(
        self,
        poi_requests: list[dict],
        provider: str = "openai",
        model: str = "gpt-4o",
        force: bool = False,
    ):
        results = []
        for req in poi_requests:
            kwargs = {
                "poi_id": req["poi_id"],
                "topic_id": req["topic_id"],
                "style_id": req["style_id"],
                "text_length": (
                    str(req.get("text_length"))
                    if req.get("text_length") is not None
                    else ""
                ),
                "provider": provider,
                "model": model,
                "force": force,
            }
            prompt_version = req.get("prompt_version")
            if isinstance(prompt_version, int):
                kwargs["prompt_version"] = prompt_version
            out = await self.get_or_generate_info_text(**kwargs)
            results.append({"poi_id": req["poi_id"], **out})
        return results
