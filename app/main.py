import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from app.api.routes import health, refdata
from app.api.routes.auth import auth
from app.api.routes.poi import poi_router
from app.api.routes.admin import admin_router
from app.api.routes.admin.auth import api_keys
from app.core.settings import settings
from app.services.generation.providers import register_providers
from fastapi.openapi.models import APIKey
from fastapi.openapi.utils import get_openapi

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
app.include_router(auth.router, tags=["Auth"])
app.include_router(poi_router, tags=["POIs"])

app.include_router(admin_router,  tags=["Admin"])

app.include_router(refdata.router, prefix="/refdata", tags=["Refdata"])
app.include_router(health.router)


# Add API Key security scheme to OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ShowMe API",
        version="1.0.0",
        description="Tourist POI backend",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    # Apply globally (all endpoints)
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"ApiKeyAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
