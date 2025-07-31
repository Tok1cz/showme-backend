from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from app.db.enums import GenerationJobStatus


class TextGenerationJobOut(BaseModel):
    task_id: UUID
    payload: dict[str, Any]
    poi_id: Optional[int] = None
    status: GenerationJobStatus
    created_at: datetime
    finished_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error_msg: Optional[str] = None

    class Config:
        orm_mode = True
