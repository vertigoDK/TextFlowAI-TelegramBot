import pytest
from app.infrastructure.database.repositories.base import BaseRepository
from app.core.models.user import User
from app.core.models.message import Message, MessageRole


class TestBaseRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, async_session):
        repo = BaseRepository(async_session, User)
        
        user = await repo.create(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            daily_limit=10,
            requests_today=5
        )
        
        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.username == "test_user"
        assert user.first_name == "Test"
        assert user.daily_limit == 10
        assert user.requests_today == 5

    @pytest.mark.asyncio
    async def test_get_by_id_existing(self, async_session):
        repo = BaseRepository(async_session, User)
        
        # Create user first
        created_user = await repo.create(
            telegram_id=123456789,
            first_name="Test"
        )
        
        # Get by ID
        retrieved_user = await repo.get_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.telegram_id == 123456789
        assert retrieved_user.first_name == "Test"

    @pytest.mark.asyncio
    async def test_get_by_id_non_existing(self, async_session):
        repo = BaseRepository(async_session, User)
        
        user = await repo.get_by_id(999)
        assert user is None

    @pytest.mark.asyncio
    async def test_update_existing(self, async_session):
        repo = BaseRepository(async_session, User)
        
        # Create user first
        user = await repo.create(
            telegram_id=123456789,
            first_name="Test",
            requests_today=0
        )
        
        # Update
        updated_user = await repo.update(
            user.id,
            first_name="Updated Test",
            requests_today=5
        )
        
        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.first_name == "Updated Test"
        assert updated_user.requests_today == 5

    @pytest.mark.asyncio
    async def test_update_non_existing(self, async_session):
        repo = BaseRepository(async_session, User)
        
        updated_user = await repo.update(999, first_name="Non-existent")
        assert updated_user is None

    @pytest.mark.asyncio
    async def test_delete_existing(self, async_session):
        repo = BaseRepository(async_session, User)
        
        # Create user first
        user = await repo.create(
            telegram_id=123456789,
            first_name="Test"
        )
        
        # Delete
        result = await repo.delete(user.id)
        assert result is True
        
        # Verify deletion
        deleted_user = await repo.get_by_id(user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_non_existing(self, async_session):
        repo = BaseRepository(async_session, User)
        
        result = await repo.delete(999)
        assert result is False

    @pytest.mark.asyncio
    async def test_repository_with_message_model(self, async_session):
        # Test that BaseRepository works with different models
        user_repo = BaseRepository(async_session, User)
        message_repo = BaseRepository(async_session, Message)
        
        # Create user first
        user = await user_repo.create(
            telegram_id=123456789,
            first_name="Test"
        )
        
        # Create message
        message = await message_repo.create(
            user_id=user.id,
            role=MessageRole.USER,
            content="Test message"
        )
        
        assert message.id is not None
        assert message.user_id == user.id
        assert message.role == MessageRole.USER
        assert message.content == "Test message"

    @pytest.mark.asyncio
    async def test_repository_model_class_attribute(self, async_session):
        repo = BaseRepository(async_session, User)
        
        assert repo.model == User
        assert repo.session == async_session