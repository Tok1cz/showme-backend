import enum

class GenerationModality(str, enum.Enum):
    text = "text"
    image = "image"
    audio = "audio"
    