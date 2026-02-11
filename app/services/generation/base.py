from abc import ABC, abstractmethod


class BaseGenerationProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs):
        pass

    @abstractmethod
    async def get_available_models(self) -> list[str]:
        """
        Return a list of available model names/IDs for this provider.
        """
        pass
