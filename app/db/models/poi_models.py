from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.enums import GeometryType, Resolution

Base = declarative_base()

class POIImage(Base):
    __tablename__ = "poi_images"
    id = Column(Integer, primary_key=True)
    poi_id = Column(BigInteger, nullable=False)
    geometry_type = Column(Enum(GeometryType, name="geometry_type_enum"), nullable=False)
    filename = Column(Text, nullable=False)
    image_url = Column(Text)
    prompt = Column(Text)
    source = Column(String)
    style_id = Column(Integer, ForeignKey("image_styles.id"), nullable=True)
    resolution = Column(Enum(Resolution, name="resolution_enum"), nullable=False)
    status = Column(String, default="ready")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # Relationship
    style = relationship("ImageStyle", lazy="joined")


class POIInfoText(Base):
    __tablename__ = "poi_info_texts"
    id = Column(Integer, primary_key=True)
    poi_id = Column(BigInteger, nullable=False)
    geometry_type = Column(Enum(GeometryType, name="geometry_type_enum"), nullable=False)
    info_text = Column(Text, nullable=False)
    prompt = Column(Text, nullable=True)
    topic_id = Column(Integer, ForeignKey("information_topics.id"), nullable=True)
    style_id = Column(Integer, ForeignKey("information_styles.id"), nullable=True)
    source = Column(String, nullable=True)
    status = Column(String, default="ready")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # Relationships
    topic = relationship("InformationTopic", lazy="joined")
    style = relationship("InformationStyle", lazy="joined")


class InformationTopic(Base):
    __tablename__ = "information_topics"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

class InformationStyle(Base):
    __tablename__ = "information_styles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

class ImageStyle(Base):
    __tablename__ = "image_styles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
