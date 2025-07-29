from sqlalchemy import Column, String, DateTime, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.enums import GenerationJobStatus
from app.db.base import Base

class TextGenerationJob(Base):
    __tablename__ = "text_generation_jobs"

    task_id = Column(PG_UUID(as_uuid=True), primary_key=True)
    payload = Column(JSON, nullable=False)
    status = Column(
    Enum(GenerationJobStatus, name="generation_job_status"),
    default=GenerationJobStatus.ready,
    server_default=GenerationJobStatus.ready,
    nullable=False,
)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    result = Column(JSON, nullable=True)
    error_msg = Column(String, nullable=True)
