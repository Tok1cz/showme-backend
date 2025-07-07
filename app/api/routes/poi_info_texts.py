from typing import Optional
from fastapi import APIRouter, Depends
from app.db.queries.poi_info_texts import (
    get_poi_info_texts,
)
from app.schemas.poi_info_text import  POIInfoTextOut
from app.db.session import get_session

router = APIRouter()


@router.get("/poi-info-texts/", response_model=list[POIInfoTextOut])
async def list_info_texts(
    poi_id: int,
    topic: Optional[str] = None,
    style: Optional[str] = None,
    session=Depends(get_session)
):
    return await get_poi_info_texts(session, poi_id, topic=topic, style=style)
