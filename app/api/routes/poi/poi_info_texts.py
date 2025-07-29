from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Union

from app.db.session import get_session
from app.schemas.poi_enhancements import InfoTextStatusResponse, InfoTextBatchRequest
from app.schemas.generation_jobs import TextGenerationJobOut, GenerationJobStatusOut

from app.services.text_generation.service import InfoTextService
from app.db.enums import TextLength
from app.db.models.generation_jobs.text_generation_job import TextGenerationJob
from app.db.queries.refdata import (
    get_information_topic_by_name,
    get_information_style_by_name,
)

router = APIRouter(
    prefix="/poi-info-texts",
)

# --- SINGLE INFO TEXT ENDPOINT ---


@router.get("/", response_model=InfoTextStatusResponse)
async def get_info_text(
    poi_id: int = Query(...),
    topic: str = Query(..., description="Topic name"),
    style: str = Query(..., description="Style name"),
    text_length: Optional[TextLength] = Query(None),
    force: bool = Query(False),
    session: AsyncSession = Depends(get_session),
):
    # Resolve names to IDs
    topic_obj = await get_information_topic_by_name(session, topic)
    if not topic_obj:
        raise HTTPException(404, f"Topic '{topic}' not found")
    style_obj = await get_information_style_by_name(session, style)
    if not style_obj:
        raise HTTPException(404, f"Style '{style}' not found")
    service = InfoTextService(session)
    result = await service.get_or_generate_info_text(
        poi_id=poi_id,
        topic_id=topic_obj.id,
        style_id=style_obj.id,
        text_length=text_length,
        force=force,
    )
    return result


# # --- BULK ENDPOINT --- #Fix
# class InfoTextBulkResponse(POIInfoTextOut):
#     status: str
#     task_id: Optional[str] = None
#     poi_id: int


@router.post("/batch", response_model=List[InfoTextStatusResponse])
async def batch_info_texts(
    requests: List[InfoTextBatchRequest],
    session: AsyncSession = Depends(get_session),
):
    service = InfoTextService(session)
    results = await service.bulk_get_or_generate_info_texts(requests)
    return results


# --- JOB STATUS ENDPOINT ---
@router.get("/status/{task_id}", response_model=TextGenerationJobOut)
async def get_info_text_job_status(
    task_id: str, session: AsyncSession = Depends(get_session)
):
    job = await session.get(TextGenerationJob, task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Task not found")
    return job
