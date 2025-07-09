from typing import List
from fastapi import APIRouter, Depends
from app.db.queries.poi_images import (
    get_images_for_poi_ids,
    get_poi_images
)
from app.core.settings import settings
from app.db.session import get_session
from app.schemas.poi_image import POIImageBatchRequest, POIImageOut
from app.api.utils.serialize import serialize_poi_image

router = APIRouter()

@router.get("/{poi_id}/images", response_model=List[POIImageOut])
async def get_images_for_poi(poi_id: int, session=Depends(get_session), ):
    images = await get_poi_images(session, poi_id)
    return [serialize_poi_image(img, base_image_url=settings.BASE_IMAGE_URL) for img in images]

@router.post("/images")
async def get_images_for_poi_batch(
    batch: POIImageBatchRequest,
    session=Depends(get_session)
):
    images = await get_images_for_poi_ids(session, batch.ids)
    # Return first image per POI (customize as needed: can return all if you want)
    result = {}
    for img in images:
        if img.poi_id not in result:
            result[img.poi_id] = (
                img.image_url if img.image_url else settings.BASE_IMAGE_URL + img.filename
            )
    # Make sure all requested ids are in the response (even if missing)
    return [
        {"poi_id": poi_id, "image_url": result.get(poi_id)}
        for poi_id in batch.ids
    ]