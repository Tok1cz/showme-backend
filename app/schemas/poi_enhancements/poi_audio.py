from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.db.enums import AudioLength, AudioQuality, EnhancementStatus
from app.schemas.refdata import RefDataOut


class POIAudioOut(BaseModel):
    id: int
    poi_id: int
    filename: Optional[str]
    audio_url: Optional[str]
    prompt: Optional[str]
    source: Optional[str]
    quality: AudioQuality
    length: AudioLength
    status: EnhancementStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    style: Optional[RefDataOut]
    orphan: Optional[bool]
    task_id: Optional[UUID]

    class Config:
        orm_mode = True


class AudioStatusResponse(BaseModel):
    status: str
    task_id: Optional[UUID] = None
    audio: Optional[POIAudioOut] = None

    class Config:
        orm_mode = True


class POIAudioBatchRequest(BaseModel):
    poi_id: int
    style: str
    quality: Optional[AudioQuality] = AudioQuality.medium
    length: Optional[AudioLength] = AudioLength.medium
