from openai import AsyncOpenAI
from app.services.text_generation.provider import TextGenerationProvider

class OpenAITextProvider(TextGenerationProvider):
    def __init__(self, api_key: str, default_model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 256),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.choices[0].message.content.strip()

    async def get_available_models(self) -> list[str]:
        models = await self.client.models.list()
        return [m.id for m in models.data]
