# from typing import List
# from fastapi import APIRouter, Depends
# from app.db.queries.poi_enhancements.poi_images import (
#     get_images_for_poi_ids,
#     get_poi_images
# )
# from app.core.settings import settings
# from app.db.session import get_session
# from app.schemas.poi_enhancements import POIImageBatchRequest, POIImageOut
# from app.api.utils.serialize import serialize_poi_image

# router = APIRouter()

# @router.get("/{poi_id}/images", response_model=List[POIImageOut])
# async def get_images_for_poi(poi_id: int, session=Depends(get_session), ):
#     images = await get_poi_images(session, poi_id)
#     return [serialize_poi_image(img, base_image_url=settings.BASE_IMAGE_URL) for img in images]

# @router.post("/images")
# async def get_images_for_poi_batch(
#     batch: POIImageBatchRequest,
#     session=Depends(get_session)
# ):
#     images = await get_images_for_poi_ids(session, batch.ids)
#     # Return first image per POI (customize as needed: can return all if you want)
#     result = {}
#     for img in images:
#         if img.poi_id not in result:
#             result[img.poi_id] = (
#                 img.image_url if img.image_url else settings.BASE_IMAGE_URL + img.filename
#             )
#     # Make sure all requested ids are in the response (even if missing)
#     return [
#         {"poi_id": poi_id, "image_url": result.get(poi_id)}
#         for poi_id in batch.ids
#     ]


from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.services.image_generation.service import ImageGenerationService
from app.schemas.poi_enhancements import POIImageOut
from app.schemas.generation_jobs import GenerationJobStatusOut
from app.db.enums import ImageResolution
from app.db.models.generation_jobs.image_generation_job import ImageGenerationJob
from typing import Optional, List, Union

router = APIRouter()

@router.get("/", response_model=Union[POIImageOut, GenerationJobStatusOut])
async def get_poi_image(
    poi_id: int = Query(...),
    style: str = Query(...),
    aspect: Optional[str] = Query(None),
    resolution: ImageResolution = Query(ImageResolution.medium),
    session: AsyncSession = Depends(get_session),
):
    print("resolution param in endpoint:", resolution, type(resolution))
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

@router.post("/batch", response_model=List[Union[POIImageOut, GenerationJobStatusOut]])
async def batch_poi_images(
    requests: List[dict] = Body(...),
    session: AsyncSession = Depends(get_session),
):
    service = ImageGenerationService(session)
    results = []
    for req in requests:
        result = await service.get_or_generate_image(
            poi_id=req["poi_id"],
            style_name=req["style"],
            aspect_name=req.get("aspect") or "",
            resolution=req.get("resolution", ImageResolution.medium),
        )
        if isinstance(result, dict) and result.get("status") == "generating":
            results.append(GenerationJobStatusOut(**result))
        else:
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
        task_id=job.task_id
    )
