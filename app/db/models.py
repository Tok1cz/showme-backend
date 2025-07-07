from sqlalchemy import BigInteger, Column, DateTime, Integer, String, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Attraction(Base):
    __tablename__ = "attractions"
    id = Column(Integer, primary_key=True, autoincrement=False)  # OSM ID
    name = Column(String)
    description = Column(String)
    tags = Column(JSON)
    geometry = Column(Geometry("GEOMETRY", srid=4326))  # Can store point, line, or polygon
    geometry_type = Column(String)

    # add more fields like type/category as needed


class POIImage(Base):
    __tablename__ = "poi_images"
    id = Column(Integer, primary_key=True)
    poi_id = Column(BigInteger, nullable=False)
    geometry_type = Column(String, nullable=False)  # POINT, POLYGON, LINESTRING, etc.
    filename = Column(Text, nullable=False)
    image_url = Column(Text)
    prompt = Column(Text)
    source = Column(String)
    style = Column(String(100), nullable=True)
    resolution = Column(String(10), nullable=False)  # 'low', 'medium', 'high'
    status = Column(String, default="ready")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# app/db/models.py


Base = declarative_base()

class POIInfoText(Base):
    __tablename__ = "poi_info_texts"
    id = Column(Integer, primary_key=True)
    poi_id = Column(BigInteger, nullable=False)
    geometry_type = Column(String, nullable=False)
    info_text = Column(Text, nullable=False)
    prompt = Column(Text, nullable=True)            # Prompt for LLM, can be null
    topic = Column(String(50), default="general")    # 'general', 'historic', etc.
    style = Column(String(100), nullable=True)       # e.g. 'encyclopedic', can be null
    source = Column(String, nullable=True)           # LLM model, admin, etc.
    status = Column(String, default="ready")         # 'ready', 'generating', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())