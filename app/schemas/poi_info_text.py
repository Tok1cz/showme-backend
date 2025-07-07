from pydantic import BaseModel
from typing import Optional

class POIInfoTextCreate(BaseModel):
    poi_id: int
    geometry_type: str
    info_text: str
    prompt: Optional[str] = None      
    topic: Optional[str] = "general"
    style: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "ready"

class POIInfoTextUpdate(BaseModel):
    info_text: Optional[str]
    prompt: Optional[str] = None       
    topic: Optional[str]
    style: Optional[str]
    source: Optional[str]
    status: Optional[str]

class POIInfoTextOut(POIInfoTextCreate):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
