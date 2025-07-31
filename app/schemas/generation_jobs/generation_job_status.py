from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from app.db.enums import GenerationJobStatus


class GenerationJobStatusOut(BaseModel):
    status: GenerationJobStatus  # "generating", "failed", etc.
    task_id: Optional[UUID] = None
    poi_id: Optional[int] = None