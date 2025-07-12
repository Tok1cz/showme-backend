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


class TextLength(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"
    very_long = "very_long"




class GenerationJobStatus(str, Enum):
    ready = "ready"
    generating = "generating"
    failed = "failed"
