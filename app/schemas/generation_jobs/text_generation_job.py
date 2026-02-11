from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

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
