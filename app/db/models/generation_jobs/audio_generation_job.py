from sqlalchemy import Column, Enum, Text, DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.db.enums import GenerationJobStatus

class AudioGenerationJob(Base):
    __tablename__ = "audio_generation_jobs"

    task_id = Column(UUID(as_uuid=True), primary_key=True)
    payload = Column(JSON, nullable=False)
    status = Column(Enum(GenerationJobStatus, name="generation_job_status"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    result = Column(JSON)
    error_msg = Column(Text)
