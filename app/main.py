import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from app.api.routes import health, refdata
from app.api.routes.poi import poi_images, pois, poi_info_texts, poi_audio
from app.api.routes.admin import (
    poi_images_cud,
    poi_info_texts_cud,
    admin_refdata,
    osm_import,
    prompt_templates,
)
from app.core.settings import settings
from app.services.generation.providers import register_providers

if settings.DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register your providers here at startup
    register_providers()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/images", StaticFiles(directory="./images"), name="images")
app.mount("/audio", StaticFiles(directory="./audio"), name="audio")

app.include_router(pois.router, prefix="/pois", tags=["POIs"])
app.include_router(poi_images.router, prefix="/pois", tags=["POI images"])
app.include_router(poi_info_texts.router, prefix="/pois", tags=["POI Info Texts"])
app.include_router(poi_audio.router, prefix="/pois", tags=["POI Audio"])

app.include_router(poi_images_cud.router, prefix="/admin", tags=["Admin"])
app.include_router(poi_info_texts_cud.router, prefix="/admin", tags=["Admin"])
app.include_router(admin_refdata.router, prefix="/admin", tags=["Admin"])
app.include_router(osm_import.router, prefix="/admin", tags=["Admin"])
app.include_router(prompt_templates.router, prefix="/admin", tags=["Admin"])

app.include_router(refdata.router, prefix="/refdata", tags=["Refdata"])
app.include_router(health.router)
