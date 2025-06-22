from typing import Protocol, List, Any
from app.core.models.message import Message


class Provider(Protocol):

    async def agenerate(
        self,
        messages: List[Message]
    ) -> dict[str, Any]: ...
