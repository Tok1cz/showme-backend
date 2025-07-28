from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.refdata import RefDataOut
from app.db.enums import EnhancementStatus, AudioQuality, AudioLength

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

    class Config:
        orm_mode = True
        