from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.services.image_generation.service import ImageGenerationService
from app.schemas.poi_enhancements import ImageStatusResponse, POIImageBatchRequest
from app.schemas.generation_jobs import GenerationJobStatusOut
from app.db.enums import ImageResolution
from app.db.models.generation_jobs.image_generation_job import ImageGenerationJob
from typing import Optional, List

router = APIRouter(
    prefix="/poi_images",
)


@router.get("/", response_model=ImageStatusResponse)
async def get_poi_image(
    poi_id: int = Query(...),
    style: str = Query(...),
    aspect: Optional[str] = Query(None),
    resolution: ImageResolution = Query(ImageResolution.medium),
    session: AsyncSession = Depends(get_session),
):
    service = ImageGenerationService(session)
    if not aspect:
        aspect = ""
    result = await service.get_or_generate_image(
        poi_id=poi_id,
        style_name=style,
        aspect_name=aspect,
        resolution=resolution,
    )
    if isinstance(result, dict) and result.get("status") == "generating":
        return GenerationJobStatusOut(**result)
    if not result:
        raise HTTPException(status_code=404, detail="Image not found or is generating")
    return result


@router.post("/batch", response_model=List[ImageStatusResponse])
async def batch_poi_images(
    requests: List[POIImageBatchRequest] = Body(...),
    session: AsyncSession = Depends(get_session),
):
    service = ImageGenerationService(session)
    results = []
    for req in requests:
        result = await service.get_or_generate_image(
            poi_id=req.poi_id,
            style_name=req.style,
            aspect_name=req.aspect or "default",
            resolution=req.resolution or ImageResolution.medium,
        )

        results.append(result)
    return results


@router.get("/status/{task_id}", response_model=GenerationJobStatusOut)
async def get_image_generation_status(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(ImageGenerationJob).where(ImageGenerationJob.task_id == task_id)
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return GenerationJobStatusOut(
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        task_id=job.task_id,
        poi_id=job.poi_id,
    )
