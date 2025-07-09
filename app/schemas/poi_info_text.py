from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.db.enums import GeometryType

class POIInfoTextCreate(BaseModel):
    poi_id: int
    geometry_type: GeometryType
    info_text: str
    prompt: Optional[str] = None
    topic: Optional[str] = "general"
    style: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "ready"

class POIInfoTextUpdate(BaseModel):
    geometry_type: Optional[GeometryType] = None
    info_text: Optional[str] = None
    prompt: Optional[str] = None
    topic: Optional[str] = None
    style: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None

class POIInfoTextOut(BaseModel):
    id: int
    poi_id: int
    geometry_type: GeometryType
    info_text: str
    prompt: Optional[str]
    topic: Optional[dict]  # {'id': int, 'name': str}
    style: Optional[dict]  # {'id': int, 'name': str}
    source: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
