from typing import Any, Dict, Optional

from pydantic import BaseModel


class AttractionBase(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None  # Parse this later
    structure_type: str  # POINT, POLYGON, LINESTRING, etc.
    lon: Optional[float] = None
    lat: Optional[float] = None
    distance_m: Optional[float] = None

    class Config:
        orm_mode = True


class AttractionList(AttractionBase):
    pass
