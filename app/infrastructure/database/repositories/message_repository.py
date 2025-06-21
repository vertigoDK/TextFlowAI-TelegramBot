from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.message import Message, MessageRole, MessageStatus
from .base import BaseRepository
from typing import Optional

class MessageRepository(BaseRepository[Message]):
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Message)

    async def create_message(
        self,
        role: MessageRole,
        content: str,
        telegram_id: int,
        status: MessageStatus = MessageStatus.PENDING,
        ai_metadata: Optional[dict] = None
    ) -> Message:

        

        return await self.create(role=role, content=content, telegram_id=telegram_id)