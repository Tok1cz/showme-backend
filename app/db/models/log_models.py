import enum  # stdlib
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from app.db.declarative_base import Base

class OSMImportStatus(enum.Enum):  # Use stdlib enum.Enum here
    started = "started"
    completed = "completed"
    failed = "failed"

class OSMImportLog(Base):
    __tablename__ = "osm_import_log"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    task_id = Column(String, nullable=True)  # Celery task/job ID
    regions = Column(JSON, nullable=False)
    files = Column(JSON, nullable=True)
    status = Column(SQLEnum(OSMImportStatus), default=OSMImportStatus.started)
    record_count = Column(Integer, nullable=True)
    error = Column(String, nullable=True)
    notes = Column(String, nullable=True)
