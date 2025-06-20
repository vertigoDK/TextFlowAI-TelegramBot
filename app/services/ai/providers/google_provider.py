from typing import override
from .base_provider import BaseProvider

class GoogleProvider(BaseProvider):

    @override
    async def agenerate(self, prompt: str) -> str:
        return ""