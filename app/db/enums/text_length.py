from enum import Enum


class TextLength(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"
    very_long = "very_long"
