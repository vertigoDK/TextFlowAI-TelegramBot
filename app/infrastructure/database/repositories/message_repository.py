from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from app.core.models.message import Message, MessageRole, MessageStatus
from .base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Message)
    
    async def create_message(
        self,
        user_id: int,
        role: MessageRole,
        content: str,
        status: MessageStatus = MessageStatus.PENDING,
        ai_metadata: Optional[dict] = None
    ) -> Message:
        """Создать новое сообщение"""
        return await self.create(
            user_id=user_id,
            role=role,
            content=content,
            status=status,
            ai_metadata=ai_metadata
        )
    
    async def get_user_messages(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Получить сообщения пользователя с пагинацией"""
        stmt = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_recent_context(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Message]:
        """Получить последние N сообщений для контекста AI (в правильном порядке)"""
        stmt = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        
        # Возвращаем в хронологическом порядке (старые -> новые)
        return list(reversed(messages))
    
    async def get_conversation_context(
        self,
        user_id: int,
        hours_back: int = 24,
        max_messages: int = 20
    ) -> List[Message]:
        """Получить контекст диалога за последние N часов"""
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        stmt = (
            select(Message)
            .where(
                Message.user_id == user_id,
                Message.created_at >= time_threshold
            )
            .order_by(Message.created_at)  # В хронологическом порядке
            .limit(max_messages)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_message_status(
        self,
        message_id: int,
        status: MessageStatus,
        ai_metadata: Optional[dict] = None
    ) -> Optional[Message]:
        """Обновить статус сообщения и метаданные"""
        if ai_metadata is not None:
            return await self.update(message_id, status=status, ai_metadata=ai_metadata)
        else:
            return await self.update(message_id, status=status)
    
    async def get_pending_messages(self, user_id: int) -> List[Message]:
        """Получить сообщения в статусе PENDING для конкретного пользователя"""
        stmt = (
            select(Message)
            .where(
                Message.user_id == user_id,
                Message.status == MessageStatus.PENDING
            )
            .order_by(Message.created_at)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_failed_messages(
        self,
        user_id: Optional[int] = None,
        hours_back: int = 24
    ) -> List[Message]:
        """Получить сообщения с ошибками за последние N часов"""
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        conditions = [
            Message.status == MessageStatus.FAILED,
            Message.created_at >= time_threshold
        ]
        
        if user_id is not None:
            conditions.append(Message.user_id == user_id)
        
        stmt = (
            select(Message)
            .where(*conditions)
            .order_by(desc(Message.created_at))
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_old_messages(
        self,
        days_old: int = 30,
        user_id: Optional[int] = None
    ) -> int:
        """Удалить старые сообщения (для очистки БД)"""
        time_threshold = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        conditions = [Message.created_at < time_threshold]
        if user_id is not None:
            conditions.append(Message.user_id == user_id)
        
        stmt = delete(Message).where(*conditions)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount
    
    async def get_user_message_count(
        self,
        user_id: int,
        hours_back: Optional[int] = None
    ) -> int:
        """Получить количество сообщений пользователя (за период или всего)"""
        conditions = [Message.user_id == user_id]
        
        if hours_back is not None:
            time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            conditions.append(Message.created_at >= time_threshold)
        
        stmt = select(Message).where(*conditions)
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        
        return len(list(messages))
    
    async def get_messages_by_role(
        self,
        user_id: int,
        role: MessageRole,
        limit: int = 50
    ) -> List[Message]:
        """Получить сообщения пользователя определенной роли"""
        stmt = (
            select(Message)
            .where(
                Message.user_id == user_id,
                Message.role == role
            )
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())