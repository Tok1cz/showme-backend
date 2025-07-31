"""TODO:
Refactor with poi_id in Respnser"""

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.services.audio_generation.service import AudioGenerationService
from app.schemas.poi_enhancements import AudioStatusResponse, POIAudioBatchRequest
from app.schemas.generation_jobs import GenerationJobStatusOut
from app.db.enums import AudioQuality, AudioLength
from app.db.models.generation_jobs.audio_generation_job import AudioGenerationJob
from typing import Optional, List

router = APIRouter(
    prefix="/poi-audio",
)


@router.get("/", response_model=AudioStatusResponse)
async def get_poi_audio(
    poi_id: int = Query(...),
    style: str = Query(...),
    quality: AudioQuality = Query(AudioQuality.medium),
    length: AudioLength = Query(AudioLength.medium),
    session: AsyncSession = Depends(get_session),
):
    service = AudioGenerationService(session)
    result = await service.get_or_generate_audio(
        poi_id=poi_id,
        style_name=style,
        quality=quality,
        length=length,
    )
    if isinstance(result, dict) and result.get("status") == "generating":
        return GenerationJobStatusOut(**result)
    if not result:
        raise HTTPException(status_code=404, detail="Audio not found or is generating")
    return result


@router.post("/batch", response_model=List[AudioStatusResponse])
async def batch_poi_audio(
    requests: List[POIAudioBatchRequest] = Body(...),
    session: AsyncSession = Depends(get_session),
):
    service = AudioGenerationService(session)
    results = []
    for req in requests:
        result = await service.get_or_generate_audio(
            poi_id=req.poi_id,
            style_name=req.style,
            quality=req.quality or AudioQuality.medium,
            length=req.length or AudioLength.medium,
        )
        if isinstance(result, dict) and result.get("status") == "generating":
            results.append(GenerationJobStatusOut(**result))
        else:
            results.append(result)
    return results


@router.get("/status/{task_id}", response_model=GenerationJobStatusOut)
async def get_audio_generation_status(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(AudioGenerationJob).where(AudioGenerationJob.task_id == task_id)
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return GenerationJobStatusOut(
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        task_id=job.task_id,
    )
