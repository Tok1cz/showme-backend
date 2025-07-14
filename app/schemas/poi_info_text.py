from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.db.enums import GeometryType, TextLength
from app.schemas.refdata import RefDataOut


class POIInfoTextCreate(BaseModel):
    poi_id: int
    info_text: str
    prompt: Optional[str] = None
    topic: Optional[str] = "general"
    style: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "ready"
    text_length: Optional[TextLength] = None

class POIInfoTextUpdate(BaseModel):
    info_text: Optional[str] = None
    prompt: Optional[str] = None
    topic: Optional[str] = None
    style: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    text_length: Optional[TextLength] = None

class POIInfoTextOut(BaseModel):
    id: int
    poi_id: int
    info_text: Optional[str]
    prompt: Optional[str]
    topic: Optional[RefDataOut]
    style: Optional[RefDataOut]
    source: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    text_length: Optional[TextLength] = None

    class Config:
        orm_mode = True