# app/services/generation/providers.py
from app.core.settings import settings
from app.services.audio_generation.providers.openai import OpenAIAudioProvider
from app.services.generation.registry import registry
from app.services.image_generation.providers.openai import OpenAIImageProvider
from app.services.text_generation.providers.openai import OpenAITextProvider


def register_providers():
    registry.register_text(
        "openai",
        OpenAITextProvider(api_key=settings.OPEN_API_KEY, default_model="gpt-4o"),
    )
    registry.register_image(
        "dalle",
        OpenAIImageProvider(api_key=settings.OPEN_API_KEY, default_model="dall-e-3"),
    )
    registry.register_audio(
        "openai",
        OpenAIAudioProvider(api_key=settings.OPEN_API_KEY, default_model="tts-1"),
    )
