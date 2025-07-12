from abc import abstractmethod
from app.services.generation.base import BaseGenerationProvider

class ImageGenerationProvider(BaseGenerationProvider):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Returns image URL or binary data.
        """
        pass
