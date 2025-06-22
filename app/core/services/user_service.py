from typing import Optional
from app.core.exceptions.base import TextFlowException
from app.core.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.core.exceptions.user import InvalidTelegramID, UserLimitExceeded, UserNotFound
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

    async def can_make_request(
        self,
        telegram_id: int
    ) -> bool:

        try:
            user = await self.user_repository.get_by_telegram_id(telegram_id=telegram_id)

            if user is None:
                return True

            return user.requests_today < user.daily_limit

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to get user: {e}")
        except Exception as e:
            raise

    async def process_user_request(
        self,
        telegram_id: int,
        first_name: str,
        username: Optional[str] = None
    ) -> User:

        self._validate_telegram_id(telegram_id=telegram_id)

        try:
            
            user = await self.user_repository.get_or_create_user(
                telegram_id=telegram_id,
                first_name=first_name,
                username=username
            )

            if user.requests_today >= user.daily_limit:
                raise UserLimitExceeded(
                    user_requests_count=user.requests_today,
                    limit_requests=user.daily_limit
                )

            await self.user_repository.increment_requests_today(telegram_id=telegram_id)
            return await self.user_repository.get_by_telegram_id(telegram_id=telegram_id)

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to process user request: {e}")
        except Exception as e:
            raise

    async def get_user_stats(
        self,
        telegram_id: int
    ) -> dict:

        self._validate_telegram_id(telegram_id=telegram_id)

        try:
            user = await self.user_repository.get_by_telegram_id(telegram_id=telegram_id)

            if user is None:
                raise UserNotFound(telegram_id=telegram_id)

            return {
                "requests_today": user.requests_today,
                "daily_limit": user.daily_limit,
                "request_remaining": user.daily_limit - user.requests_today,
                "limit_reached": user.requests_today >= user.daily_limit
            }

        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to get user stats: {e}")
        except Exception as e:
            raise

    async def reset_all_daily_limits(self) -> int:
        try:
            return await self.user_repository.reset_daily_limits()
        except SQLAlchemyError as e:
            raise TextFlowException(f"Failed to reset daily limits: {e}")
        except Exception as e:
            raise

    def _validate_telegram_id(self, telegram_id: int) -> None:
        """Валидация Telegram ID (должен быть положительным числом)"""
        
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            raise InvalidTelegramID()
        
        # Telegram ID обычно от 9 до 10 цифр
        if not (100000000 <= telegram_id <= 9999999999):
            raise InvalidTelegramID()
