# app/services/audio_generation/provider.py

from typing import Optional

from openai import AsyncOpenAI

from app.services.audio_generation.provider import AudioGenerationProvider


class OpenAIAudioProvider(AudioGenerationProvider):
    def __init__(self, api_key: str, default_model: str = "tts-1"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(
        self, prompt: str, model: str = None, voice: Optional[str] = None, **kwargs
    ) -> bytes:
        response = await self.client.audio.speech.create(
            model=model or self.default_model,
            input=prompt,
            voice=voice or "alloy",
            response_format=kwargs.get("response_format", "mp3"),
            speed=kwargs.get("speed", 1.0),
        )
        # For speech, OpenAI returns a response object with .content (audio bytes)
        # Save or stream .content as your audio file
        return response.content

    async def get_available_models(self) -> list[str]:
        models = await self.client.models.list()
        # Filter for audio models (OpenAI uses "tts-1" etc. for audio)
        return [m.id for m in models.data if m.id.startswith("tts")]
