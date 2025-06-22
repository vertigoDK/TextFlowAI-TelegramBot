from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from aiogram.types import TelegramObject
from app.core.services.user_service import UserService


class UserMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        try:

            if not hasattr(event, "from_user") or not event.from_user:
                return await handler(event, data)

            telegram_user = event.from_user

            user = await self.user_service.handle_new_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
            )

            data["user"] = user

            return await handler(event, data)
        except Exception as e:
            raise
