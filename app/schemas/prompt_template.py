from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.enums import TextLength


class PromptTemplateBase(BaseModel):
    provider: str
    model: str
    topic_id: int
    style_id: int
    version: int
    template: str
    text_length: Optional[TextLength] = None


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    topic_id: Optional[int] = None
    style_id: Optional[int] = None
    version: Optional[int] = None
    template: Optional[str] = None


class PromptTemplateOut(PromptTemplateBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
