from typing import List, Optional
from pydantic import BaseModel
from app.db.enums import GeometryType, ImageResolution
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.refdata import RefDataOut
from app.db.enums import EnhancementStatus, ImageResolution

class POIImageOut(BaseModel):
    id: int
    poi_id: int
    filename: Optional[str]
    image_url: Optional[str]
    prompt: Optional[str]
    source: Optional[str]
    resolution: ImageResolution
    status: Optional[EnhancementStatus]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    style: Optional[RefDataOut]
    aspect: Optional[RefDataOut]
    orphan: Optional[bool]

    class Config:
        orm_mode = True

class POIImageCreate(BaseModel):
    poi_id: int
    geometry_type: GeometryType
    filename: str
    resolution: ImageResolution
    style: Optional[str] = None
    image_url: Optional[str] = None
    prompt: Optional[str] = None
    source: Optional[str] = None
    status: Optional[EnhancementStatus] = EnhancementStatus.active


class POIImageUpdate(BaseModel):
    resolution: Optional[str]
    style: Optional[str] = None
    image_url: Optional[str]
    prompt: Optional[str]
    source: Optional[str]
    status: Optional[EnhancementStatus] = EnhancementStatus.active


class POIImageBatchRequest(BaseModel):
    ids: List[int]
