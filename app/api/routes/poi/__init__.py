from fastapi import APIRouter, Depends

from app.services.auth.dependencies import get_current_user
from .poi_audio import router as poi_audio_router
from .poi_images import router as poi_images_router
from .pois import router as pois_router
from .poi_info_texts import router as poi_info_texts_router

poi_router = APIRouter(
    prefix="/pois",
    dependencies=[Depends(get_current_user)],
)
poi_router.include_router(poi_audio_router)
poi_router.include_router(poi_images_router)
poi_router.include_router(poi_info_texts_router)
poi_router.include_router(pois_router)