from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.db.enums import EnhancementStatus, TextLength
from app.schemas.refdata import RefDataOut


class POIInfoTextCreate(BaseModel):
    poi_id: int
    info_text: str
    prompt: Optional[str] = None
    topic: Optional[str] = "general"
    style: Optional[str] = None
    source: Optional[str] = None
    status: Optional[EnhancementStatus] = EnhancementStatus.active
    text_length: Optional[TextLength] = None


class POIInfoTextUpdate(BaseModel):
    info_text: Optional[str] = None
    prompt: Optional[str] = None
    topic: Optional[str] = None
    style: Optional[str] = None
    source: Optional[str] = None
    status: Optional[EnhancementStatus] = None
    text_length: Optional[TextLength] = None


class POIInfoTextOut(BaseModel):
    id: int
    poi_id: int
    info_text: Optional[str]
    prompt: Optional[str]
    topic: Optional[RefDataOut]
    style: Optional[RefDataOut]
    source: Optional[str]
    status: Optional[EnhancementStatus]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    text_length: Optional[TextLength] = None
    audio_id: Optional[int]  # or nested POIAudio if you want
    task_id: Optional[UUID]

    class Config:
        orm_mode = True


class InfoTextStatusResponse(BaseModel):
    status: str
    task_id: Optional[UUID] = None
    poi_id: int
    info_text: Optional[POIInfoTextOut] = None


class InfoTextBatchRequest(BaseModel):
    poi_id: int
    topic: str
    style: str
    text_length: Optional[TextLength] = None
    force: bool = False
