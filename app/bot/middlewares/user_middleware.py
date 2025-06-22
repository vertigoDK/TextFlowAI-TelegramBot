from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from aiogram.types import TelegramObject
from app.core.services.container import Container


class UserMiddleware(BaseMiddleware):
    def __init__(self, container: Container):
        self.container = container

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

            # Создаем новый user_service для этого запроса
            user_service = await self.container.get_user_service()

            user = await user_service.handle_new_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
            )

            data["user"] = user

            return await handler(event, data)
        except Exception as e:
            raise
