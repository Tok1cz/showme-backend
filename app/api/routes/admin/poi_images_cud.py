from fastapi import APIRouter, Depends, HTTPException
from app.db.queries.poi_images import (
    create_poi_image,
    update_poi_image,
    delete_poi_image,
    get_poi_images
)
from app.core.settings import settings
from app.db.session import get_session
from app.schemas.poi_image import POIImageCreate, POIImageUpdate, POIImageOut
router = APIRouter()

@router.get("/{poi_id}/images")
async def get_images_for_poi(poi_id: int, session=Depends(get_session)):
    images = await get_poi_images(session, poi_id)
    return [
        {
            "id": img.id,
            "url": (img.image_url if img.image_url else settings.base_image_url + img.filename),
            "resolution": img.resolution,
            "style": img.style,
            "geometry_type": img.geometry_type,
            "status": img.status,
        }
        for img in images
    ]
# ADMIN ENDPOINT!!!
@router.post("/images/", response_model=POIImageOut, status_code=201)
async def create_image(image: POIImageCreate, session=Depends(get_session)):
    created = await create_poi_image(session, **image.dict())
    return created
# ADMIN ENDPOINT!!!
@router.patch("/images/{image_id}", response_model=POIImageOut)
async def update_image(image_id: int, image: POIImageUpdate, session=Depends(get_session)):
    updated = await update_poi_image(session, image_id, **image.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Image not found")
    return updated
# ADMIN ENDPOINT!!!
@router.delete("/images/{image_id}", status_code=204)
async def delete_image(image_id: int, session=Depends(get_session)):
    img = await get_poi_images(session, image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    await delete_poi_image(session, image_id)
    return