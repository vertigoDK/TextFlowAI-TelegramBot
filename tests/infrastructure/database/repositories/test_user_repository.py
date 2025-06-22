import pytest
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.core.models.user import User


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_get_by_telegram_id_existing(self, async_session):
        repo = UserRepository(async_session)
        
        # Create user first
        user = await repo.create(
            telegram_id=123456789,
            first_name="Test",
            username="test_user"
        )
        
        # Get by telegram_id
        retrieved_user = await repo.get_by_telegram_id(123456789)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.telegram_id == 123456789
        assert retrieved_user.first_name == "Test"
        assert retrieved_user.username == "test_user"

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_non_existing(self, async_session):
        repo = UserRepository(async_session)
        
        user = await repo.get_by_telegram_id(999999999)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_or_create_user_new_user(self, async_session):
        repo = UserRepository(async_session)
        
        user = await repo.get_or_create_user(
            telegram_id=123456789,
            first_name="New User",
            username="new_user"
        )
        
        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.first_name == "New User"
        assert user.username == "new_user"

    @pytest.mark.asyncio
    async def test_get_or_create_user_existing_user(self, async_session):
        repo = UserRepository(async_session)
        
        # Create user first
        original_user = await repo.create(
            telegram_id=123456789,
            first_name="Original User",
            username="original_user"
        )
        
        # Try to get_or_create with same telegram_id
        retrieved_user = await repo.get_or_create_user(
            telegram_id=123456789,
            first_name="Different Name",  # This should be ignored
            username="different_user"     # This should be ignored
        )
        
        assert retrieved_user.id == original_user.id
        assert retrieved_user.telegram_id == 123456789
        assert retrieved_user.first_name == "Original User"  # Original data preserved
        assert retrieved_user.username == "original_user"    # Original data preserved

    @pytest.mark.asyncio
    async def test_get_or_create_user_without_username(self, async_session):
        repo = UserRepository(async_session)
        
        user = await repo.get_or_create_user(
            telegram_id=123456789,
            first_name="Test User"
        )
        
        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.first_name == "Test User"
        assert user.username is None

    @pytest.mark.asyncio
    async def test_update_user_info_existing(self, async_session):
        repo = UserRepository(async_session)
        
        # Create user first
        user = await repo.create(
            telegram_id=123456789,
            first_name="Original Name",
            username="original_username"
        )
        
        # Update user info
        updated_user = await repo.update_user_info(
            telegram_id=123456789,
            first_name="Updated Name",
            username="updated_username"
        )
        
        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.telegram_id == 123456789
        assert updated_user.first_name == "Updated Name"
        assert updated_user.username == "updated_username"

    @pytest.mark.asyncio
    async def test_update_user_info_non_existing(self, async_session):
        repo = UserRepository(async_session)
        
        updated_user = await repo.update_user_info(
            telegram_id=999999999,
            first_name="Non-existent User"
        )
        
        assert updated_user is None

    @pytest.mark.asyncio
    async def test_increment_requests_today(self, async_session):
        repo = UserRepository(async_session)
        
        # Create user with specific request count
        user = await repo.create(
            telegram_id=123456789,
            first_name="Test",
            requests_today=5
        )
        
        # Increment requests
        result = await repo.increment_requests_today(123456789)
        assert result is True
        
        # Verify increment
        updated_user = await repo.get_by_telegram_id(123456789)
        assert updated_user.requests_today == 6

    @pytest.mark.asyncio
    async def test_increment_requests_today_non_existing_user(self, async_session):
        repo = UserRepository(async_session)
        
        # This should succeed even for non-existing user (though it won't affect anything)
        result = await repo.increment_requests_today(999999999)
        assert result is True

    @pytest.mark.asyncio
    async def test_reset_daily_limits_with_users_having_requests(self, async_session):
        repo = UserRepository(async_session)
        
        # Create users with different request counts
        user1 = await repo.create(
            telegram_id=111111111,
            first_name="User1",
            requests_today=5
        )
        user2 = await repo.create(
            telegram_id=222222222,
            first_name="User2",
            requests_today=0  # Should not be reset
        )
        user3 = await repo.create(
            telegram_id=333333333,
            first_name="User3",
            requests_today=10
        )
        
        # Reset daily limits
        reset_count = await repo.reset_daily_limits()
        
        assert reset_count == 2  # Only user1 and user3 should be reset
        
        # Verify resets
        updated_user1 = await repo.get_by_telegram_id(111111111)
        updated_user2 = await repo.get_by_telegram_id(222222222)
        updated_user3 = await repo.get_by_telegram_id(333333333)
        
        assert updated_user1.requests_today == 0
        assert updated_user2.requests_today == 0
        assert updated_user3.requests_today == 0

    @pytest.mark.asyncio
    async def test_reset_daily_limits_no_users_with_requests(self, async_session):
        repo = UserRepository(async_session)
        
        # Create users with zero requests
        await repo.create(
            telegram_id=111111111,
            first_name="User1",
            requests_today=0
        )
        await repo.create(
            telegram_id=222222222,
            first_name="User2",
            requests_today=0
        )
        
        # Reset daily limits
        reset_count = await repo.reset_daily_limits()
        
        assert reset_count == 0

    @pytest.mark.asyncio
    async def test_repository_inheritance(self, async_session):
        repo = UserRepository(async_session)
        
        # Should inherit all BaseRepository methods
        assert hasattr(repo, 'create')
        assert hasattr(repo, 'get_by_id')
        assert hasattr(repo, 'update')
        assert hasattr(repo, 'delete')
        assert repo.model == User