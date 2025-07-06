from fastapi import APIRouter, Depends
from app.db.session import get_session
from app.db.queries import get_n_nearest_attractions
from app.schemas import AttractionList

router = APIRouter()


@router.get("/nearest")
async def get_nearest_pois(
    lat: float, lon: float, n: int = 10, session=Depends(get_session)
):
    results = await get_n_nearest_attractions(session, lat, lon, n)

    return [AttractionList(**poi) for poi in results]
