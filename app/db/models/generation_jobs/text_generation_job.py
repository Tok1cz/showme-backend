from datetime import datetime

from sqlalchemy import JSON, BigInteger, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base

from app.db.declarative_base import Base
from app.db.enums import GenerationJobStatus


class TextGenerationJob(Base):
    __tablename__ = "text_generation_jobs"

    task_id = Column(PG_UUID(as_uuid=True), primary_key=True)
    poi_id = Column(BigInteger, nullable=True)
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
