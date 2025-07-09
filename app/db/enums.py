from enum import Enum

class GeometryType(str, Enum):
    point = "POINT"
    polygon = "POLYGON"
    linestring = "LINESTRING"
    multipolygon = "MULTIPOLYGON"
    multilinestring = "MULTILINESTRING"

class Resolution(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
