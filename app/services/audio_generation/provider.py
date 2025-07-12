from abc import abstractmethod
from app.services.generation.base import BaseGenerationProvider

class AudioGenerationProvider(BaseGenerationProvider):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Returns audio URL or binary data.
        """
        pass
