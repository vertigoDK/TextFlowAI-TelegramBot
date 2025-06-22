from typing import Any, Dict, List
from aiogram import Router
from aiogram import types

from app.core.models.message import Message, MessageRole
from app.core.models.user import User
from app.core.services.ai.generator import AIGenerator
from app.core.services.user_service import UserService
from app.core.services.message_service import MessageService

router = Router()


@router.message()
async def handle_text_message(
    message: types.Message,
    user: User,
    user_service: UserService,
    message_service: MessageService,
    conversation_ai: AIGenerator,
    ) -> None:

        if message.text is None:
            return

        if not await user_service.can_make_request(user.telegram_id):
            await message.answer("You have reached your daily limit.")
            return 

        user_message: Message = await message_service.create_message(
            telegram_id=user.telegram_id,
            role=MessageRole.USER,
            content=message.text,
        )

        recent_messages: List[Message] = await message_service.get_conversation_context(
            telegram_id=user.telegram_id,
        )

        response: Dict[str, Any] = await conversation_ai.agenerate(recent_messages)


        await message.answer(f"{response['content']}")
