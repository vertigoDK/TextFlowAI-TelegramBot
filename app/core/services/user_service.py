from typing import Optional
from app.core.exceptions.base import TextFlowException
from app.core.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.core.exceptions.user import InvalidTelegramID
from sqlalchemy.exc import SQLAlchemyError

class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def handle_new_user(
        self,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None
    ) -> User:
    
        self._validate_telegram_id(telegram_id)

        try:
            user = await self.user_repository.get_or_create_user(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username
            )

            return user
        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to process user: {e}")
        except Exception as e:
            raise

    def _validate_telegram_id(self, telegram_id: int) -> None:
        """Валидация Telegram ID (должен быть положительным числом)"""
        
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            raise InvalidTelegramID()
        
        # Telegram ID обычно от 9 до 10 цифр
        if not (100000000 <= telegram_id <= 9999999999):
            raise InvalidTelegramID()
