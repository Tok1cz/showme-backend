from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.enums import EnhancementStatus, ImageResolution
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class POIImage(Base):
    __tablename__ = "poi_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    poi_id: Mapped[int] = mapped_column(
        ForeignKey("planet_osm_point.osm_id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(Text, nullable=True)
    resolution: Mapped[ImageResolution] = mapped_column(
        Enum(ImageResolution, name="image_resolution"),
        nullable=False,
        default=ImageResolution.medium,
    )
    status: Mapped[EnhancementStatus] = mapped_column(
        Enum(EnhancementStatus, name="enhancement_status"),
        nullable=False,
        default=EnhancementStatus.active,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    style_id: Mapped[int] = mapped_column(ForeignKey("image_styles.id"))
    aspect_id: Mapped[int] = mapped_column(
        ForeignKey("image_aspects.id"), nullable=True
    )
    orphan: Mapped[bool] = mapped_column(Boolean, default=False)

    task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("image_generation_jobs.task_id"), nullable=True)

    # Relationships to helper/reference tables
    style = relationship("ImageStyle", lazy="joined")
    aspect = relationship("ImageAspect", lazy="joined")
    image_generation_job = relationship("ImageGenerationJob", lazy="joined", uselist=False, foreign_keys=[task_id])


class ImageStyle(Base):
    __tablename__ = "image_styles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)


class ImageAspect(Base):
    __tablename__ = "image_aspects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    images = relationship("POIImage", back_populates="aspect")
