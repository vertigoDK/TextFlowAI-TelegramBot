from typing import List, Any
from app.core.models.message import Message
from .prompt_builders.base_builder import PromptBuilder
from .providers.base_provider import Provider


class AIGenerator[P: Provider, B: PromptBuilder]:
    def __init__(self, provider: P, prompt_builder: B):
        self.provider = provider
        self.prompt_builder = prompt_builder

    async def agenerate(self, messages: List[Message]) -> dict[str, Any]:
        prompt = self.prompt_builder.build(messages)
        return await self.provider.agenerate(prompt)
