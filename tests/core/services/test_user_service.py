import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
from app.core.services.user_service import UserService
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.core.models.user import User
from app.core.exceptions.user import UserLimitExceeded, UserNotFound, InvalidTelegramID
from app.core.exceptions.base import TextFlowException
from sqlalchemy.exc import SQLAlchemyError


class TestUserService:
    @pytest_asyncio.fixture
    async def mock_user_repository(self):
        """Mock UserRepository for testing"""
        return AsyncMock(spec=UserRepository)

    @pytest_asyncio.fixture
    async def user_service(self, mock_user_repository):
        """Create UserService with mocked repository"""
        return UserService(mock_user_repository)

    @pytest_asyncio.fixture
    async def sample_user(self):
        """Sample user for testing"""
        user = Mock(spec=User)
        user.id = 1
        user.telegram_id = 123456789
        user.first_name = "Test User"
        user.username = "test_user"
        user.daily_limit = 20
        user.requests_today = 5
        return user

    @pytest.mark.asyncio
    async def test_handle_new_user_success(self, user_service, mock_user_repository, sample_user):
        # Setup
        mock_user_repository.get_or_create_user.return_value = sample_user
        
        # Execute
        result = await user_service.handle_new_user(
            telegram_id=123456789,
            first_name="Test User",
            username="test_user"
        )
        
        # Assert
        assert result == sample_user
        mock_user_repository.get_or_create_user.assert_called_once_with(
            telegram_id=123456789,
            first_name="Test User",
            username="test_user"
        )

    @pytest.mark.asyncio
    async def test_handle_new_user_without_username(self, user_service, mock_user_repository, sample_user):
        # Setup
        mock_user_repository.get_or_create_user.return_value = sample_user
        
        # Execute
        result = await user_service.handle_new_user(
            telegram_id=123456789,
            first_name="Test User"
        )
        
        # Assert
        assert result == sample_user
        mock_user_repository.get_or_create_user.assert_called_once_with(
            telegram_id=123456789,
            first_name="Test User",
            username=None
        )

    @pytest.mark.asyncio
    async def test_handle_new_user_invalid_telegram_id(self, user_service, mock_user_repository):
        # Execute & Assert
        with pytest.raises(InvalidTelegramID):
            await user_service.handle_new_user(
                telegram_id=0,  # Invalid telegram_id
                first_name="Test User"
            )

    @pytest.mark.asyncio
    async def test_handle_new_user_sqlalchemy_error(self, user_service, mock_user_repository):
        # Setup
        mock_user_repository.get_or_create_user.side_effect = SQLAlchemyError("DB Error")
        
        # Execute & Assert
        with pytest.raises(TextFlowException, match="Failed to process user"):
            await user_service.handle_new_user(
                telegram_id=123456789,
                first_name="Test User"
            )

    @pytest.mark.asyncio
    async def test_can_make_request_user_exists_within_limit(self, user_service, mock_user_repository, sample_user):
        # Setup - user has 5 requests out of 20 limit
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        
        # Execute
        result = await user_service.can_make_request(123456789)
        
        # Assert
        assert result is True
        mock_user_repository.get_by_telegram_id.assert_called_once_with(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_can_make_request_user_exists_at_limit(self, user_service, mock_user_repository, sample_user):
        # Setup - user has reached daily limit
        sample_user.requests_today = 20
        sample_user.daily_limit = 20
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        
        # Execute
        result = await user_service.can_make_request(123456789)
        
        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_can_make_request_user_not_exists(self, user_service, mock_user_repository):
        # Setup - user doesn't exist
        mock_user_repository.get_by_telegram_id.return_value = None
        
        # Execute
        result = await user_service.can_make_request(123456789)
        
        # Assert
        assert result is True  # New users can make requests

    @pytest.mark.asyncio
    async def test_can_make_request_sqlalchemy_error(self, user_service, mock_user_repository):
        # Setup
        mock_user_repository.get_by_telegram_id.side_effect = SQLAlchemyError("DB Error")
        
        # Execute & Assert
        with pytest.raises(TextFlowException, match="Failed to get user"):
            await user_service.can_make_request(123456789)

    @pytest.mark.asyncio
    async def test_process_user_request_success(self, user_service, mock_user_repository, sample_user):
        # Setup
        updated_user = Mock(spec=User)
        updated_user.requests_today = 6  # Incremented
        
        mock_user_repository.get_or_create_user.return_value = sample_user
        mock_user_repository.increment_requests_today.return_value = True
        mock_user_repository.get_by_telegram_id.return_value = updated_user
        
        # Execute
        result = await user_service.process_user_request(
            telegram_id=123456789,
            first_name="Test User",
            username="test_user"
        )
        
        # Assert
        assert result == updated_user
        mock_user_repository.get_or_create_user.assert_called_once()
        mock_user_repository.increment_requests_today.assert_called_once_with(telegram_id=123456789)
        mock_user_repository.get_by_telegram_id.assert_called_once_with(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_process_user_request_limit_exceeded(self, user_service, mock_user_repository, sample_user):
        # Setup - user has reached limit
        sample_user.requests_today = 20
        sample_user.daily_limit = 20
        mock_user_repository.get_or_create_user.return_value = sample_user
        
        # Execute & Assert
        with pytest.raises(UserLimitExceeded) as exc_info:
            await user_service.process_user_request(
                telegram_id=123456789,
                first_name="Test User"
            )
        
        # Assert exception details
        assert exc_info.value.user_request_count == 20
        assert exc_info.value.limit_requests == 20

    @pytest.mark.asyncio
    async def test_process_user_request_invalid_telegram_id(self, user_service):
        # Execute & Assert
        with pytest.raises(InvalidTelegramID):
            await user_service.process_user_request(
                telegram_id=0,
                first_name="Test User"
            )

    @pytest.mark.asyncio
    async def test_get_user_stats_success(self, user_service, mock_user_repository, sample_user):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        
        # Execute
        result = await user_service.get_user_stats(123456789)
        
        # Assert
        expected_stats = {
            "requests_today": 5,
            "daily_limit": 20,
            "request_remaining": 15,
            "limit_reached": False
        }
        assert result == expected_stats

    @pytest.mark.asyncio
    async def test_get_user_stats_limit_reached(self, user_service, mock_user_repository, sample_user):
        # Setup - user at limit
        sample_user.requests_today = 20
        sample_user.daily_limit = 20
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        
        # Execute
        result = await user_service.get_user_stats(123456789)
        
        # Assert
        expected_stats = {
            "requests_today": 20,
            "daily_limit": 20,
            "request_remaining": 0,
            "limit_reached": True
        }
        assert result == expected_stats

    @pytest.mark.asyncio
    async def test_get_user_stats_user_not_found(self, user_service, mock_user_repository):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(UserNotFound) as exc_info:
            await user_service.get_user_stats(123456789)
        
        assert exc_info.value.telegram_id == 123456789

    @pytest.mark.asyncio
    async def test_get_user_stats_invalid_telegram_id(self, user_service):
        # Execute & Assert
        with pytest.raises(InvalidTelegramID):
            await user_service.get_user_stats(0)

    @pytest.mark.asyncio
    async def test_get_user_stats_sqlalchemy_error(self, user_service, mock_user_repository):
        # Setup
        mock_user_repository.get_by_telegram_id.side_effect = SQLAlchemyError("DB Error")
        
        # Execute & Assert
        with pytest.raises(TextFlowException, match="Failed to get user stats"):
            await user_service.get_user_stats(123456789)

    @pytest.mark.asyncio
    async def test_reset_all_daily_limits_success(self, user_service, mock_user_repository):
        # Setup
        mock_user_repository.reset_daily_limits.return_value = 5  # 5 users reset
        
        # Execute
        result = await user_service.reset_all_daily_limits()
        
        # Assert
        assert result == 5
        mock_user_repository.reset_daily_limits.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_all_daily_limits_sqlalchemy_error(self, user_service, mock_user_repository):
        # Setup
        mock_user_repository.reset_daily_limits.side_effect = SQLAlchemyError("DB Error")
        
        # Execute & Assert
        with pytest.raises(TextFlowException, match="Failed to reset daily limits"):
            await user_service.reset_all_daily_limits()

    @pytest.mark.asyncio
    async def test_user_service_repository_dependency(self, mock_user_repository):
        # Execute
        service = UserService(mock_user_repository)
        
        # Assert
        assert service.user_repository == mock_user_repository