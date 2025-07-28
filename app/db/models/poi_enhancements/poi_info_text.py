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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.enums import EnhancementStatus
from app.db.base import Base

class POIInfoText(Base):
    __tablename__ = "poi_info_texts"

    id: Mapped[int] = mapped_column(primary_key=True)
    poi_id: Mapped[int] = mapped_column(ForeignKey("planet_osm_point.osm_id"), nullable=False)
    info_text: Mapped[str] = mapped_column(Text, nullable=False)
    prompt: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    status: Mapped[EnhancementStatus] = mapped_column(Enum(EnhancementStatus, name="enhancement_status"), nullable=False, default=EnhancementStatus.active)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey("information_topics.id"))
    style_id: Mapped[int] = mapped_column(ForeignKey("information_styles.id"))
    audio_id: Mapped[int] = mapped_column(ForeignKey("poi_audio.id"), nullable=True)

    # Relationships to helper/reference tables
    topic = relationship("InformationTopic", lazy="joined")
    style = relationship("InformationStyle", lazy="joined")
    audio = relationship("POIAudio", lazy="joined", uselist=False, foreign_keys=[audio_id])


class InformationTopic(Base):
    __tablename__ = "information_topics"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)


class InformationStyle(Base):
    __tablename__ = "information_styles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
