from typing import Any, List, Optional, Dict
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.message_repository import (
    MessageRepository,
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
        ai_metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:

        self._validate_message_input(telegram_id=telegram_id, content=content)

        try:
            user = await self.user_repository.get_by_telegram_id(
                telegram_id=telegram_id
            )

            if not user:
                raise UserNotFound(telegram_id=telegram_id)

            message: Message = await self.message_repository.create_message(
                user_id=user.id,
                role=role,
                content=content,
                ai_metadata=ai_metadata,
            )

            return message

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to create message: {e}")
        except Exception as e:
            raise

    async def get_conversation_context(
        self, telegram_id: int, context_limit: int = 10
    ) -> List[Message]:
        validate_telegram_id(telegram_id=telegram_id)

        try:
            user = await self.user_repository.get_by_telegram_id(
                telegram_id=telegram_id
            )

            if not user:
                raise UserNotFound(telegram_id=telegram_id)

            return await self.message_repository.get_recent_context(
                user_id=user.id,
                limit=context_limit,
            )

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to get conversation context: {e}")
        except Exception as e:
            raise

    async def get_user_messages(
        self, telegram_id: int, limit: int = 20, offset: int = 0
    ) -> List[Message]:
        validate_telegram_id(telegram_id=telegram_id)

        try:
            user = await self.user_repository.get_by_telegram_id(
                telegram_id=telegram_id
            )

            if not user:
                raise UserNotFound(telegram_id=telegram_id)

            return await self.message_repository.get_user_messages(
                user_id=user.id,
                limit=limit,
                offset=offset,
            )

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to get user messages: {e}")
        except Exception as e:
            raise

    async def cleanup_old_messages(
        self, days_old: int = 30, telegram_id: Optional[int] = None
    ) -> int:
        try:
            user_id = None

            if telegram_id is not None:
                user = await self.user_repository.get_by_telegram_id(
                    telegram_id=telegram_id
                )

                if not user:
                    raise UserNotFound(telegram_id=telegram_id)
                user_id = user.id

            deleted_count = await self.message_repository.delete_old_messages(
                days_old=days_old,
                user_id=user_id,
            )

            return deleted_count

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to cleanup old messages: {e}")
        except Exception as e:
            raise

    def _validate_message_input(self, telegram_id: int, content: str) -> None:
        validate_telegram_id(telegram_id=telegram_id)

        content = content.strip()
        if not content:
            raise InvalidMessageData("Message content cannot be empty")

        if len(content) > 4096:
            raise InvalidMessageData("Message content too long (max 4096 characters)")
