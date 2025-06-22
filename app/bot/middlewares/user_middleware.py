from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from app.core.services.user_service import UserService

class UserMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def __call__(
        self, handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]], event: Any, data: Dict[str, Any]
    ) -> Any:
        telegram_user = event.from_user
        
        user = await self.user_service.handle_new_user(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name
        )
        
        data["user"] = user
        
        return await handler(event, data)