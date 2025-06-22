from typing import Protocol, List
from app.core.models.message import Message


class PromptBuilder(Protocol):

    def build(self, messages: List[Message]) -> str: ...
