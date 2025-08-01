from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.enums import EnhancementStatus, TextLength
from app.db.declarative_base import Base
from typing import Optional
from app.db.models.generation_jobs.text_generation_job import TextGenerationJob


class POIInfoText(Base):
    __tablename__ = "poi_info_texts"

    id: Mapped[int] = mapped_column(primary_key=True)
    poi_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    info_text: Mapped[str] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[EnhancementStatus] = mapped_column(Enum(EnhancementStatus, name="enhancement_status"), nullable=False, default=EnhancementStatus.active)
    text_length: Mapped[TextLength] = mapped_column(Enum(TextLength, name="text_length"), nullable=False, default=TextLength.medium)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey("information_topics.id"), nullable=True)
    style_id: Mapped[int] = mapped_column(ForeignKey("information_styles.id"), nullable=True)
    audio_id: Mapped[int] = mapped_column(ForeignKey("poi_audio.id"), nullable=True)
    task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("text_generation_jobs.task_id"), nullable=True)
    provider: Mapped[str] = mapped_column(Text, nullable=True, default="openai")
    model: Mapped[str] = mapped_column(Text, nullable=True, default="gpt-4o")
    prompt_version: Mapped[int] = mapped_column(Integer, nullable=True, default=1)
    # Relationships to helper/reference tables
    topic = relationship("InformationTopic", lazy="joined")
    style = relationship("InformationStyle", lazy="joined")
    audio = relationship("POIAudio", lazy="joined", uselist=False, foreign_keys=[audio_id])
    text_generation_job = relationship("TextGenerationJob", lazy="joined", uselist=False, foreign_keys=[task_id])

class InformationTopic(Base):
    __tablename__ = "information_topics"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)


class InformationStyle(Base):
    __tablename__ = "information_styles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
