from fastapi import APIRouter, Depends, HTTPException
from app.db.queries.poi_images import (
    get_poi_images
)
from app.core.settings import settings
from app.db.session import get_session
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