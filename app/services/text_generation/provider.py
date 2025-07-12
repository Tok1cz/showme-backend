from abc import abstractmethod
from app.services.generation.base import BaseGenerationProvider



class TextGenerationProvider(BaseGenerationProvider):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
