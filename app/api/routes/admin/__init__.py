from fastapi import APIRouter, Depends

from app.services.auth.permissions import admin_required

from .admin_refdata import router as admin_refdata_router
from .auth.api_keys import router as api_keys_router
from .osm_import import router as osm_import_router
from .poi_images_cud import router as poi_images_cud_router
from .poi_info_texts_cud import router as poi_info_texts_cud_router
from .prompt_templates import router as prompt_templates_router

admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(admin_required)],
)

admin_router.include_router(api_keys_router)
admin_router.include_router(admin_refdata_router)
admin_router.include_router(osm_import_router)
admin_router.include_router(prompt_templates_router)
admin_router.include_router(poi_images_cud_router)
admin_router.include_router(poi_info_texts_cud_router)
