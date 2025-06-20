from abc import ABC, abstractmethod

class BaseProvider(ABC):
    
    @abstractmethod
    async def agenerate(self, prompt: str) -> str:
        ...