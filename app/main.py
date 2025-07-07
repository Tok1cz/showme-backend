from fastapi import FastAPI
import logging

from fastapi.staticfiles import StaticFiles
from app.api.routes import poi_images, pois, health, poi_info_texts
from app.api.routes.admin import poi_images_cud, poi_info_texts_cud
from app.core.settings import settings

if settings.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(pois.router, prefix="/pois", tags=["POIs"])
app.include_router(poi_images_cud.router, prefix="/pois", tags=["POIs"])
app.include_router(poi_images.router, prefix="/pois", tags=["POIs"])
app.include_router(poi_info_texts_cud.router, prefix="/pois", tags=["POIs"])
app.include_router(poi_info_texts.router, prefix="/pois", tags=["POIs"])
app.include_router(health.router)