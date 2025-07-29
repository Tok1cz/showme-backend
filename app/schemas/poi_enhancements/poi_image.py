from typing import List, Optional
from pydantic import BaseModel
from app.db.enums import ImageResolution
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.refdata import RefDataOut
from app.db.enums import EnhancementStatus, ImageResolution
from uuid import UUID


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
    task_id: Optional[UUID]

    class Config:
        orm_mode = True


class POIImageCreate(BaseModel):
    poi_id: int
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
    poi_id: int
    style: str
    aspect: Optional[str] = None
    resolution: ImageResolution = ImageResolution.medium

class ImageStatusResponse(BaseModel):
    status: str
    task_id: Optional[UUID] = None
    image: Optional[POIImageOut] = None