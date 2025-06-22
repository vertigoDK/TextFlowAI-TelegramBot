from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..models.message import Message, MessageRole
from .user_service import UserService
from ..services.message_service import MessageService
from ...infrastructure.database.repositories.message_repository import MessageRepository
from ...infrastructure.database.repositories.user_repository import UserRepository


class CabinetService:
    """Service for personal cabinet functionality"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.message_repository = MessageRepository(session)
        self.user_service = UserService(self.user_repository)
        self.message_service = MessageService(self.user_repository, self.message_repository)
    
    async def get_profile_info(self, telegram_id: int) -> Dict[str, str]:
        """Get user profile information"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        profile_data = {
            "full_name": user.first_name,
            "username": f"@{user.username}" if user.username else "Not set",
            "telegram_id": str(user.telegram_id),
            "member_since": user.created_at.strftime("%B %d, %Y"),
            "account_status": "🟢 Active" if user.requests_today < user.daily_limit else "🔴 Limited"
        }
        
        return profile_data
    
    async def get_daily_usage_stats(self, telegram_id: int) -> Dict[str, str]:
        """Get daily usage statistics"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        remaining = max(0, user.daily_limit - user.requests_today)
        usage_percentage = (user.requests_today / user.daily_limit) * 100
        
        stats = {
            "requests_used": str(user.requests_today),
            "daily_limit": str(user.daily_limit),
            "remaining_requests": str(remaining),
            "usage_percentage": f"{usage_percentage:.1f}%",
            "limit_status": "🔴 Limit Reached" if remaining == 0 else "🟢 Available"
        }
        
        return stats
    
    async def get_weekly_stats(self, telegram_id: int) -> Dict[str, str]:
        """Get weekly usage statistics"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        # Get messages from the last 7 days (168 hours)
        weekly_messages = await self.message_repository.get_user_message_count(
            user.id, 
            hours_back=168
        )
        
        # Get user messages only (not assistant responses)
        user_messages = await self.message_repository.get_messages_by_role_count(
            user.id,
            MessageRole.USER,
            hours_back=168
        )
        
        stats = {
            "total_messages": str(weekly_messages),
            "user_requests": str(user_messages),
            "ai_responses": str(weekly_messages - user_messages),
            "daily_average": f"{user_messages / 7:.1f}",
            "period": "Last 7 days"
        }
        
        return stats
    
    async def get_all_time_stats(self, telegram_id: int) -> Dict[str, str]:
        """Get all-time usage statistics"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        total_messages = await self.message_repository.get_user_message_count(user.id)
        user_messages = await self.message_repository.get_messages_by_role_count(
            user.id, 
            MessageRole.USER
        )
        ai_messages = total_messages - user_messages
        
        # Calculate days since registration
        days_registered = (datetime.now() - user.created_at).days + 1
        avg_daily_requests = user_messages / days_registered if days_registered > 0 else 0
        
        stats = {
            "total_messages": str(total_messages),
            "user_requests": str(user_messages),
            "ai_responses": str(ai_messages),
            "days_registered": str(days_registered),
            "avg_daily_requests": f"{avg_daily_requests:.1f}",
            "most_active_day": "Today" if user.requests_today > 0 else "Not today"
        }
        
        return stats
    
    async def get_recent_messages(
        self, 
        telegram_id: int, 
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, str]]:
        """Get recent message history"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        messages = await self.message_repository.get_user_messages(
            user.id,
            limit=limit,
            offset=offset
        )
        
        formatted_messages = []
        for msg in messages:
            role_emoji = "👤" if msg.role == MessageRole.USER else "🤖"
            formatted_msg = {
                "id": str(msg.id),
                "role": f"{role_emoji} {msg.role.value.title()}",
                "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                "timestamp": msg.created_at.strftime("%m/%d %H:%M"),
                "full_content": msg.content
            }
            formatted_messages.append(formatted_msg)
        
        return formatted_messages
    
    async def get_message_history_count(self, telegram_id: int) -> int:
        """Get total count of user messages for pagination"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        return await self.message_repository.get_user_message_count(user.id)
    
    async def export_message_history(self, telegram_id: int) -> str:
        """Export message history as formatted text"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        messages = await self.message_repository.get_user_messages(user.id, limit=1000)
        
        export_text = f"📄 Message History Export\n"
        export_text += f"👤 User: {user.first_name}\n"
        export_text += f"📅 Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"📊 Total Messages: {len(messages)}\n"
        export_text += "=" * 50 + "\n\n"
        
        for i, msg in enumerate(messages, 1):
            role_name = "You" if msg.role == MessageRole.USER else "AI Assistant"
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            export_text += f"[{i}] {role_name} ({timestamp}):\n"
            export_text += f"{msg.content}\n\n"
            
            if i % 50 == 0:  # Add separator every 50 messages
                export_text += "-" * 30 + "\n\n"
        
        return export_text
    
    async def clear_message_history(self, telegram_id: int) -> bool:
        """Clear user's message history"""
        try:
            user = await self.user_service.handle_new_user(telegram_id, "", "")
            await self.message_repository.delete_all_user_messages(user.id)
            return True
        except Exception:
            return False
    
    async def get_account_settings(self, telegram_id: int) -> Dict[str, str]:
        """Get account settings information"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        settings = {
            "daily_limit": str(user.daily_limit),
            "current_usage": str(user.requests_today),
            "account_type": "Standard User",
            "data_retention": "Indefinite",
            "last_reset": "Daily at midnight UTC",
            "account_id": str(user.id)
        }
        
        return settings
    
    async def get_usage_patterns(self, telegram_id: int) -> Dict[str, str]:
        """Get usage pattern analysis"""
        user = await self.user_service.handle_new_user(telegram_id, "", "")
        
        # Get recent activity patterns - today vs yesterday
        today_messages = user.requests_today
        
        # Get yesterday's messages (24-48 hours back)
        yesterday_messages = await self.message_repository.get_messages_by_role_count(
            user.id,
            MessageRole.USER,
            hours_back=48
        ) - await self.message_repository.get_messages_by_role_count(
            user.id,
            MessageRole.USER,
            hours_back=24
        )
        
        patterns = {
            "today_requests": str(today_messages),
            "yesterday_requests": str(yesterday_messages),
            "trend": "📈 Increasing" if today_messages > yesterday_messages else "📉 Decreasing" if today_messages < yesterday_messages else "➡️ Stable",
            "peak_usage": "Throughout the day",
            "preferred_time": "Current session",
            "consistency": "Regular user" if user.requests_today > 0 else "Casual user"
        }
        
        return patterns