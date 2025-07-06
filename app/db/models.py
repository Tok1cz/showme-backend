from sqlalchemy import Column, Integer, String, JSON
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base

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
