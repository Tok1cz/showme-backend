from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.enums import GenerationJobStatus


class GenerationJobStatusOut(BaseModel):
    status: GenerationJobStatus  # "generating", "failed", etc.
    task_id: Optional[UUID] = None
    poi_id: Optional[int] = None
