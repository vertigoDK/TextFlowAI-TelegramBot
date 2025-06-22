import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from app.infrastructure.database.repositories.message_repository import MessageRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.core.models.message import Message, MessageRole
from app.core.models.user import User


class TestMessageRepository:
    @pytest_asyncio.fixture
    async def test_user(self, async_session):
        """Create a test user for message tests"""
        user_repo = UserRepository(async_session)
        return await user_repo.create(
            telegram_id=123456789,
            first_name="Test User",
            username="test_user"
        )

    @pytest.mark.asyncio
    async def test_create_message(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        message = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Hello, world!",
            ai_metadata={"model": "gemini", "tokens": 100}
        )
        
        assert message.id is not None
        assert message.user_id == test_user.id
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert message.ai_metadata == {"model": "gemini", "tokens": 100}

    @pytest.mark.asyncio
    async def test_create_message_without_metadata(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        message = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="AI response"
        )
        
        assert message.id is not None
        assert message.user_id == test_user.id
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "AI response"
        assert message.ai_metadata is None

    @pytest.mark.asyncio
    async def test_get_user_messages(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create multiple messages
        message1 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="First message"
        )
        message2 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Second message"
        )
        message3 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Third message"
        )
        
        # Get user messages
        messages = await repo.get_user_messages(test_user.id)
        
        assert len(messages) == 3
        # Check that all messages are returned
        contents = [msg.content for msg in messages]
        assert "First message" in contents
        assert "Second message" in contents
        assert "Third message" in contents

    @pytest.mark.asyncio
    async def test_get_user_messages_with_pagination(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create multiple messages
        for i in range(5):
            await repo.create_message(
                user_id=test_user.id,
                role=MessageRole.USER,
                content=f"Message {i}"
            )
        
        # Test limit
        messages = await repo.get_user_messages(test_user.id, limit=3)
        assert len(messages) == 3
        
        # Test offset
        messages = await repo.get_user_messages(test_user.id, limit=2, offset=2)
        assert len(messages) == 2

    @pytest.mark.asyncio
    async def test_get_recent_context(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create messages in sequence
        message1 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="First"
        )
        message2 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Second"
        )
        message3 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Third"
        )
        
        # Get recent context
        context = await repo.get_recent_context(test_user.id, limit=2)
        
        assert len(context) == 2
        # Check that we get 2 most recent messages
        contents = [msg.content for msg in context]
        assert len(set(contents)) == 2  # Should be 2 different messages

    @pytest.mark.asyncio
    async def test_get_conversation_context(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create messages
        message1 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Context message 1"
        )
        message2 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Context message 2"
        )
        
        # Get conversation context
        context = await repo.get_conversation_context(test_user.id, hours_back=1)
        
        assert len(context) == 2
        # Should be in chronological order
        assert context[0].id == message1.id
        assert context[1].id == message2.id

    @pytest.mark.asyncio
    async def test_get_pending_messages(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create messages
        message1 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Pending message 1"
        )
        message2 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Pending message 2"
        )
        
        # Get pending messages
        pending = await repo.get_pending_messages(test_user.id)
        
        assert len(pending) == 2
        assert pending[0].id == message1.id
        assert pending[1].id == message2.id

    @pytest.mark.asyncio
    async def test_get_failed_messages(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create messages
        message1 = await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Failed message"
        )
        
        # Get failed messages
        failed = await repo.get_failed_messages(user_id=test_user.id)
        
        # Since we don't have status field anymore, this should return all messages
        assert len(failed) >= 1

    @pytest.mark.asyncio
    async def test_get_failed_messages_all_users(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create message
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Message"
        )
        
        # Get failed messages for all users
        failed = await repo.get_failed_messages()
        
        assert len(failed) >= 1

    @pytest.mark.asyncio
    async def test_delete_old_messages(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create some messages
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Message to delete"
        )
        
        # Delete messages older than 0 days (should delete all)
        deleted_count = await repo.delete_old_messages(days_old=0)
        
        assert deleted_count >= 1
        
        # Verify deletion
        remaining_messages = await repo.get_user_messages(test_user.id)
        assert len(remaining_messages) == 0

    @pytest.mark.asyncio
    async def test_delete_old_messages_specific_user(self, async_session, test_user):
        repo = MessageRepository(async_session)
        user_repo = UserRepository(async_session)
        
        # Create another user
        user2 = await user_repo.create(
            telegram_id=987654321,
            first_name="User 2"
        )
        
        # Create messages for both users
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="User 1 message"
        )
        await repo.create_message(
            user_id=user2.id,
            role=MessageRole.USER,
            content="User 2 message"
        )
        
        # Delete old messages for user 1 only
        deleted_count = await repo.delete_old_messages(days_old=0, user_id=test_user.id)
        
        assert deleted_count == 1
        
        # Verify user 1 messages deleted, user 2 messages remain
        user1_messages = await repo.get_user_messages(test_user.id)
        user2_messages = await repo.get_user_messages(user2.id)
        
        assert len(user1_messages) == 0
        assert len(user2_messages) == 1

    @pytest.mark.asyncio
    async def test_get_user_message_count_total(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create messages
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Message 1"
        )
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Message 2"
        )
        
        # Get total count
        count = await repo.get_user_message_count(test_user.id)
        assert count == 2

    @pytest.mark.asyncio
    async def test_get_user_message_count_with_time_filter(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create message
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="Recent message"
        )
        
        # Get count for last 1 hour
        count = await repo.get_user_message_count(test_user.id, hours_back=1)
        assert count == 1
        
        # Get count for last 0 hours (should be 0)
        count = await repo.get_user_message_count(test_user.id, hours_back=0)
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_messages_by_role(self, async_session, test_user):
        repo = MessageRepository(async_session)
        
        # Create messages with different roles
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="User message 1"
        )
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.ASSISTANT,
            content="Assistant message"
        )
        await repo.create_message(
            user_id=test_user.id,
            role=MessageRole.USER,
            content="User message 2"
        )
        
        # Get only user messages
        user_messages = await repo.get_messages_by_role(test_user.id, MessageRole.USER)
        assert len(user_messages) == 2
        assert all(msg.role == MessageRole.USER for msg in user_messages)
        
        # Get only assistant messages
        assistant_messages = await repo.get_messages_by_role(test_user.id, MessageRole.ASSISTANT)
        assert len(assistant_messages) == 1
        assert all(msg.role == MessageRole.ASSISTANT for msg in assistant_messages)

    @pytest.mark.asyncio
    async def test_repository_inheritance(self, async_session):
        repo = MessageRepository(async_session)
        
        # Should inherit all BaseRepository methods
        assert hasattr(repo, 'create')
        assert hasattr(repo, 'get_by_id')
        assert hasattr(repo, 'update')
        assert hasattr(repo, 'delete')
        assert repo.model == Message