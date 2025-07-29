from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.declarative_base import Base
from app.db.enums import GenerationModality
from datetime import datetime

class GenerationSource(Base):
    __tablename__ = "generation_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(Text, nullable=False)
    modality: Mapped[GenerationModality] = mapped_column(Enum(GenerationModality, name="generation_modality"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)