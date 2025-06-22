from typing import Any, Dict, List
from aiogram import Router
from aiogram import types

from app.core.models.message import Message, MessageRole
from app.core.models.user import User
from app.core.services.container import Container

router = Router()


@router.message()
async def handle_text_message(
    message: types.Message,
    user: User,
    container: Container,
    ) -> None:

        if message.text is None:
            return

        user_service = await container.get_user_service()
        message_service = await container.get_message_service()
        conversation_ai = container.conversation_ai

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

        await user_service.process_user_request(
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            username=user.username,
        )

        response: Dict[str, Any] = await conversation_ai.agenerate(recent_messages)

        await message_service.create_message(
            telegram_id=user.telegram_id,
            role=MessageRole.ASSISTANT,
            content=response['content'],
            ai_metadata=response,
        )

        await message.answer(f"{response['content']}")
