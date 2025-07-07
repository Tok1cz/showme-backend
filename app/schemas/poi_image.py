from pydantic import BaseModel
from typing import Optional

class POIImageCreate(BaseModel):
    poi_id: int
    geometry_type: str
    filename: str
    resolution: str
    style: Optional[str] = None
    image_url: Optional[str] = None
    prompt: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "ready"

class POIImageUpdate(BaseModel):
    resolution: Optional[str]
    style: Optional[str]
    image_url: Optional[str]
    prompt: Optional[str]
    source: Optional[str]
    status: Optional[str]

class POIImageOut(POIImageCreate):
    id: int
