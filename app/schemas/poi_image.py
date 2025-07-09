from typing import List, Optional
from pydantic import BaseModel
from app.db.enums import GeometryType, Resolution
from datetime import datetime

class POIImageCreate(BaseModel):
    poi_id: int
    geometry_type: GeometryType
    filename: str
    resolution: Resolution
    style: Optional[str] = None
    image_url: Optional[str] = None
    prompt: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "ready"


class POIImageUpdate(BaseModel):
    resolution: Optional[str]
    style: Optional[str] = None
    image_url: Optional[str]
    prompt: Optional[str]
    source: Optional[str]
    status: Optional[str]

class POIImageOut(BaseModel):
    id: int
    poi_id: int
    geometry_type: GeometryType
    filename: str
    resolution: Resolution
    style: Optional[dict]  # {'id': int, 'name': str}
    image_url: Optional[str]
    prompt: Optional[str]
    source: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class POIImageBatchRequest(BaseModel):
    ids: List[int]
