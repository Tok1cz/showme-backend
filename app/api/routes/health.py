from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.db.session import get_session

router = APIRouter()


@router.get("/health", tags=["Health"])
async def healthcheck(session=Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "db_error", "details": str(e)}
