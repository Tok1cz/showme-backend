from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Union

from app.db.session import get_session
from app.schemas.poi_info_text import POIInfoTextOut
from app.schemas.text_generation_job import TextGenerationJobOut, InfoTextStatusResponse
from app.services.text_generation.service import InfoTextService
from app.db.enums import TextLength
from app.db.models.text_generation_job import TextGenerationJob

router = APIRouter(prefix="/poi-info-texts", tags=["POIs"])

# --- SINGLE INFO TEXT ENDPOINT ---
class InfoTextResponse(POIInfoTextOut):
    status: str
    task_id: Optional[str] = None

@router.get("/", response_model=POIInfoTextOut) #@router.get("/", response_model=Union[POIInfoTextOut, InfoTextResponse])
async def get_info_text(
    poi_id: int = Query(...),
    topic_id: int = Query(...),
    style_id: int = Query(...),
    text_length: Optional[TextLength] = Query(None),
    force: bool = Query(False),
    session: AsyncSession = Depends(get_session),
):
    service = InfoTextService(session)
    result = await service.get_or_generate_info_text(
        poi_id=poi_id,
        topic_id=topic_id,
        style_id=style_id,
        text_length=text_length,
        force=force
    )
    # If you want to wrap the result in a schema, you can map it here
    return result

# --- BULK ENDPOINT ---
class InfoTextBulkResponse(POIInfoTextOut):
    status: str
    task_id: Optional[str] = None
    poi_id: int

@router.post("/batch", response_model=List[InfoTextBulkResponse])
async def batch_info_texts(
    requests: List[dict],
    session: AsyncSession = Depends(get_session),
):
    service = InfoTextService(session)
    results = await service.bulk_get_or_generate_info_texts(requests)
    return results

# --- JOB STATUS ENDPOINT ---
@router.get("/status/{task_id}", response_model=TextGenerationJobOut)
async def get_info_text_job_status(
    task_id: str,
    session: AsyncSession = Depends(get_session)
):
    job = await session.get(TextGenerationJob, task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Task not found")
    return job
