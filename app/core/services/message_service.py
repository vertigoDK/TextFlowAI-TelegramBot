from ast import Dict
from typing import Any, List
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.message_repository import (
    MessageRepository,
    MessageStatus,
    MessageRole,
    Message,
)
from app.core.exceptions.user import UserNotFound
from app.core.exceptions.message import InvalidMessageData
from app.core.exceptions.base import TextFlowException
from sqlalchemy.exc import SQLAlchemyError
from app.utils.validators import validate_telegram_id

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

        self._validate_message_input(telegram_id=telegram_id, content=content)

        try:
            user = await self.user_repository.get_by_telegram_id(telegram_id=telegram_id)

            if not user:
                raise UserNotFound(telegram_id=telegram_id)

            message: Message = await self.message_repository.create_message(
                user_id=user.id,
                role=role,
                content=content,
                status=status,
                ai_metadata=ai_metadata,
            )

            return message

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to create message: {e}")
        except Exception as e:
            raise

    async def get_conversation_context(
        self,
        telegram_id: int,
        context_limit: int = 10
    ) -> List[Message]:
        validate_telegram_id(telegram_id=telegram_id)
        return [Message()]


    def _validate_message_input(self, telegram_id: int, content: str) -> None:
        validate_telegram_id(telegram_id=telegram_id)
        
        content = content.strip()
        if not content:
            raise InvalidMessageData("Message content cannot be empty")
        
        if len(content) > 4096:
            raise InvalidMessageData("Message content too long (max 4096 characters)")