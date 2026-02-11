from typing import Dict

from app.services.audio_generation.provider import AudioGenerationProvider
from app.services.image_generation.provider import ImageGenerationProvider
from app.services.text_generation.provider import TextGenerationProvider


class ProviderRegistry:
    def __init__(self):
        self.text_providers: Dict[str, "TextGenerationProvider"] = {}
        self.image_providers: Dict[str, "ImageGenerationProvider"] = {}
        self.audio_providers: Dict[str, "AudioGenerationProvider"] = {}

    def register_text(self, name: str, provider: "TextGenerationProvider"):
        self.text_providers[name] = provider

    def get_text(self, name: str) -> "TextGenerationProvider":
        return self.text_providers[name]

    def register_image(self, name: str, provider: "ImageGenerationProvider"):
        self.image_providers[name] = provider

    def get_image(self, name: str) -> "ImageGenerationProvider":
        return self.image_providers[name]

    def register_audio(self, name: str, provider: "AudioGenerationProvider"):
        self.audio_providers[name] = provider

    def get_audio(self, name: str) -> "AudioGenerationProvider":
        return self.audio_providers[name]


registry = ProviderRegistry()
