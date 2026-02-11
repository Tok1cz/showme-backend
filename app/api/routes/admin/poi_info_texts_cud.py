from fastapi import APIRouter, Depends, HTTPException

from app.db.queries.poi_enhancements.poi_info_texts import (
    create_poi_info_text,
    delete_poi_info_text,
    get_poi_info_text_by_id,
    update_poi_info_text,
)
from app.db.session import get_session
from app.schemas.poi_enhancements import (
    POIInfoTextCreate,
    POIInfoTextOut,
    POIInfoTextUpdate,
)

router = APIRouter()


@router.post("/poi-info-texts/", response_model=POIInfoTextOut, status_code=201)
async def create_info_text(info: POIInfoTextCreate, session=Depends(get_session)):
    created = await create_poi_info_text(session, **info.dict())
    return created


@router.patch("/poi-info-texts/{info_id}", response_model=POIInfoTextOut)
async def update_info_text(
    info_id: int, info: POIInfoTextUpdate, session=Depends(get_session)
):
    updated = await update_poi_info_text(
        session, info_id, **info.dict(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Info text not found")
    return updated


@router.delete("/poi-info-texts/{info_id}", status_code=204)
async def delete_info_text(info_id: int, session=Depends(get_session)):
    info = await get_poi_info_text_by_id(session, info_id)
    if not info:
        raise HTTPException(status_code=404, detail="Info text not found")
    await delete_poi_info_text(session, info_id)
    return
