from datetime import datetime
from sqlalchemy import Text, Integer, Boolean, ForeignKey, Enum, DateTime, Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.enums import EnhancementStatus, AudioQuality, AudioLength

class POIAudio(Base):
    __tablename__ = "poi_audio"

    id: Mapped[int] = mapped_column(primary_key=True)
    poi_id: Mapped[int] = mapped_column(ForeignKey("planet_osm_point.osm_id"), nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    quality: Mapped[AudioQuality] = mapped_column(Enum(AudioQuality, name="audio_quality"), nullable=False, default=AudioQuality.medium)
    length: Mapped[AudioLength] = mapped_column(Enum(AudioLength, name="audio_length"), nullable=False, default=AudioLength.medium)
    status: Mapped[EnhancementStatus] = mapped_column(Enum(EnhancementStatus, name="enhancement_status"), nullable=False, default=EnhancementStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    style_id: Mapped[int] = mapped_column(ForeignKey("information_styles.id"))
    orphan: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships to helper/reference tables
    style = relationship("InformationStyle", lazy="joined")


class AudioVoice(Base):
    __tablename__ = "audio_voices"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)