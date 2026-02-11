# app/services/image_generation/provider.py

from openai import AsyncOpenAI

from app.services.image_generation.provider import ImageGenerationProvider


class OpenAIImageProvider(ImageGenerationProvider):
    def __init__(self, api_key: str, default_model: str = "dall-e-3"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(self, prompt: str, model: str = None, **kwargs) -> dict:
        response = await self.client.images.generate(
            model=model or self.default_model,
            prompt=prompt,
            n=kwargs.get("n", 1),  # number of images to generate
            size=kwargs.get("size", "1024x1024"),
            # quality=kwargs.get("quality", "standard"), not in dall-e.2
            #     style=kwargs.get("style", None),
        )
        # Typically you'll want to return the image URL and possibly base64 content
        # Here, just return the full response for extensibility
        return response.data if hasattr(response, "data") else response

    async def get_available_models(self) -> list[str]:
        models = await self.client.models.list()
        # Filter for image models (OpenAI uses "dall-e-3" etc. for images)
        return [m.id for m in models.data if m.id.startswith("dall-e")]
