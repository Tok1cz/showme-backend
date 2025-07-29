from sqlalchemy import select


async def resolve_enhancement_status(enhancement, job_model, session) -> str:
    # enhancement: SQLAlchemy row (POIImage, POIAudio, POIInfoText)
    # job_model: matching job model (ImageGenerationJob, AudioGenerationJob, TextGenerationJob)
    # session: AsyncSession

    if enhancement.task_id is None:
        return "ready"  # Or "manual" if you want to distinguish manual uploads
    stmt = select(job_model.status).where(job_model.task_id == enhancement.task_id)
    result = await session.execute(stmt)
    status = result.scalar_one_or_none()
    return status.value if status and hasattr(status, "value") else str(status or "unknown")
