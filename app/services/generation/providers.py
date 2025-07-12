# app/services/generation/providers.py
from app.services.generation.registry import registry
from app.services.text_generation.providers.openai import OpenAITextProvider
from app.core.settings import settings

def register_providers():
    registry.register_text(
        "openai",
        OpenAITextProvider(api_key=settings.OPEN_API_KEY, default_model="gpt-4o")
    )
