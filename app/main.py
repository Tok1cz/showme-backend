from fastapi import FastAPI
import logging

from fastapi.staticfiles import StaticFiles
from app.api.routes import health
from app.api.routes.poi import poi_images, pois, poi_info_texts
from app.api.routes.admin import poi_images_cud, poi_info_texts_cud, admin_refdata, osm_import
from app.core.settings import settings

if settings.DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(pois.router, prefix="/pois", tags=["POIs"])
app.include_router(poi_images.router, prefix="/pois", tags=["POIs"])
app.include_router(poi_info_texts.router, prefix="/pois", tags=["POIs"])

app.include_router(poi_images_cud.router, prefix="/admin", tags=["Admin"])
app.include_router(poi_info_texts_cud.router, prefix="/admin", tags=["Admin"])
app.include_router(admin_refdata.router, prefix="/admin", tags=["Admin"])
app.include_router(osm_import.router, prefix="/admin", tags=["Admin"])

app.include_router(health.router)