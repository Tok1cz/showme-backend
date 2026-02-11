from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class OSMImportLogOut(BaseModel):
    id: int
    started_at: datetime
    finished_at: Optional[datetime]
    task_id: Optional[str]
    status: str
    regions: List[str]
    files: Optional[Dict[str, str]]
    record_count: Optional[int]
    error: Optional[str]
    notes: Optional[str]

    class Config:
        orm_mode = True


class OSMImportJobSubmitOut(BaseModel):
    status: str  # e.g. "submitted"
    task_id: str


class OSMImportJobStatusOut(BaseModel):
    task_id: str
    state: str  # Celery: PENDING, STARTED, SUCCESS, FAILURE, etc.
    result: Optional[Any] = None  # Can be more strictly typed if you wish
    info: Optional[str] = None
