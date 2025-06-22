from ast import Dict
from typing import Any
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.message_repository import (
    MessageRepository,
    MessageStatus,
    MessageRole,
    Message,
)


class MessageService:

    def __init__(
        self, user_repository: UserRepository, message_repository: MessageRepository
    ) -> None:
        self.user_repository = user_repository
        self.message_repository = message_repository

    async def create_message(
        self,
        telegram_id: int,
        role: MessageRole,
        content: str,
        status: MessageStatus = MessageStatus.PENDING,
        ai_metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        return Message()
