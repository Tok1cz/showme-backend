from fastapi import APIRouter, Depends, HTTPException, Query

from app import celery_app
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult
from app.services.osm_import.runner import run_osm_import_task
from app.db.models.log_models import OSMImportLog
from app.schemas.admin_osm_import import OSMImportJobSubmitOut, OSMImportLogOut

router = APIRouter(prefix="/admin/osm-import", tags=["Admin"])


@router.post("/run", response_model=OSMImportJobSubmitOut)
async def trigger_osm_import():
    celery_result = run_osm_import_task.delay()
    return OSMImportJobSubmitOut(status="submitted", task_id=celery_result.id)

from app.schemas.admin_osm_import import OSMImportJobStatusOut

@router.get("/job-status", response_model=OSMImportJobStatusOut)
async def get_osm_import_job_status(task_id: str = Query(...)):
    async_result = AsyncResult(task_id)
    return OSMImportJobStatusOut(
        task_id=task_id,
        state=async_result.state,
        result=async_result.result if async_result.successful() else None,
        info=str(async_result.info) if async_result.info else None,
    )