from fastapi import APIRouter, Depends, HTTPException

from app.db.queries.poi import get_n_nearest_attractions, get_poi_by_id
from app.db.session import get_session
from app.schemas.poi import AttractionList
from app.services.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/nearest")
async def get_nearest_pois(
    lat: float, lon: float, n: int = 10, skip: int = 0, session=Depends(get_session)
):
    results = await get_n_nearest_attractions(session, lat, lon, n, skip)
    return [AttractionList(**poi) for poi in results]


@router.get("/poi-detail/{poi_id}", response_model=AttractionList)
async def get_poi_detail(poi_id: int, session=Depends(get_session)):
    poi = await get_poi_by_id(session, poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    return AttractionList(**poi)
