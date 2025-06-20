from typing import override
from .base_provider import BaseProvider
from google import genai

class GoogleProvider(BaseProvider):

    def __init__(self, api_key: str):
        self.api_key = api_key

    @override
    async def agenerate(self, prompt: str) -> str:
        return ""
