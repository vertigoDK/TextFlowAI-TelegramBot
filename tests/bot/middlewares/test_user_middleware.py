import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
from aiogram.types import Message as TelegramMessage, User as TelegramUser
from app.bot.middlewares.user_middleware import UserMiddleware
from app.core.services.container import Container
from app.core.models.user import User


class TestUserMiddleware:
    @pytest_asyncio.fixture
    async def mock_container(self):
        """Mock container with user service"""
        container = Mock(spec=Container)
        user_service = AsyncMock()
        user_service.handle_new_user.return_value = Mock(spec=User)
        container.get_user_service.return_value = user_service
        return container

    @pytest_asyncio.fixture
    async def mock_telegram_user(self):
        """Mock Telegram user"""
        user = Mock(spec=TelegramUser)
        user.id = 123456789
        user.username = "test_user"
        user.first_name = "Test"
        return user

    @pytest_asyncio.fixture
    async def mock_event_with_user(self, mock_telegram_user):
        """Mock event with user"""
        event = Mock()
        event.from_user = mock_telegram_user
        return event

    @pytest_asyncio.fixture
    async def mock_event_without_user(self):
        """Mock event without user"""
        event = Mock()
        event.from_user = None
        return event

    @pytest_asyncio.fixture
    async def mock_handler(self):
        """Mock handler function"""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_middleware_initialization(self, mock_container):
        # Execute
        middleware = UserMiddleware(mock_container)
        
        # Assert
        assert middleware.container == mock_container

    @pytest.mark.asyncio
    async def test_middleware_with_user(self, mock_container, mock_event_with_user, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        data = {}
        
        mock_user = Mock(spec=User)
        user_service = AsyncMock()
        user_service.handle_new_user.return_value = mock_user
        mock_container.get_user_service.return_value = user_service
        
        # Execute
        result = await middleware(mock_handler, mock_event_with_user, data)
        
        # Assert
        mock_container.get_user_service.assert_called_once()
        user_service.handle_new_user.assert_called_once_with(
            telegram_id=123456789,
            username="test_user",
            first_name="Test"
        )
        
        # Verify user is added to data
        assert "user" in data
        assert data["user"] == mock_user
        
        # Verify handler is called
        mock_handler.assert_called_once_with(mock_event_with_user, data)

    @pytest.mark.asyncio
    async def test_middleware_without_user(self, mock_container, mock_event_without_user, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        data = {}
        
        # Execute
        result = await middleware(mock_handler, mock_event_without_user, data)
        
        # Assert - should skip user processing
        mock_container.get_user_service.assert_not_called()
        
        # Verify handler is still called
        mock_handler.assert_called_once_with(mock_event_without_user, data)
        
        # Verify no user in data
        assert "user" not in data

    @pytest.mark.asyncio
    async def test_middleware_event_without_from_user_attribute(self, mock_container, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        event = Mock()
        # Remove from_user attribute entirely
        del event.from_user
        data = {}
        
        # Execute
        result = await middleware(mock_handler, event, data)
        
        # Assert - should skip user processing
        mock_container.get_user_service.assert_not_called()
        mock_handler.assert_called_once_with(event, data)

    @pytest.mark.asyncio
    async def test_middleware_with_user_no_username(self, mock_container, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        
        telegram_user = Mock(spec=TelegramUser)
        telegram_user.id = 123456789
        telegram_user.username = None  # No username
        telegram_user.first_name = "Test"
        
        event = Mock()
        event.from_user = telegram_user
        data = {}
        
        mock_user = Mock(spec=User)
        user_service = AsyncMock()
        user_service.handle_new_user.return_value = mock_user
        mock_container.get_user_service.return_value = user_service
        
        # Execute
        result = await middleware(mock_handler, event, data)
        
        # Assert
        user_service.handle_new_user.assert_called_once_with(
            telegram_id=123456789,
            username=None,
            first_name="Test"
        )

    @pytest.mark.asyncio
    async def test_middleware_creates_new_user_service(self, mock_container, mock_event_with_user, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        data = {}
        
        # Execute
        await middleware(mock_handler, mock_event_with_user, data)
        
        # Assert - new user service should be created for each request
        mock_container.get_user_service.assert_called_once()

    @pytest.mark.asyncio
    async def test_middleware_exception_handling(self, mock_container, mock_event_with_user, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        data = {}
        
        user_service = AsyncMock()
        user_service.handle_new_user.side_effect = Exception("User service error")
        mock_container.get_user_service.return_value = user_service
        
        # Execute & Assert
        with pytest.raises(Exception, match="User service error"):
            await middleware(mock_handler, mock_event_with_user, data)

    @pytest.mark.asyncio
    async def test_middleware_returns_handler_result(self, mock_container, mock_event_with_user, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        data = {}
        expected_result = "handler_result"
        mock_handler.return_value = expected_result
        
        # Execute
        result = await middleware(mock_handler, mock_event_with_user, data)
        
        # Assert
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_middleware_preserves_existing_data(self, mock_container, mock_event_with_user, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        data = {"existing_key": "existing_value"}
        
        mock_user = Mock(spec=User)
        user_service = AsyncMock()
        user_service.handle_new_user.return_value = mock_user
        mock_container.get_user_service.return_value = user_service
        
        # Execute
        await middleware(mock_handler, mock_event_with_user, data)
        
        # Assert - existing data preserved, user added
        assert data["existing_key"] == "existing_value"
        assert data["user"] == mock_user

    @pytest.mark.asyncio
    async def test_middleware_user_data_type(self, mock_container, mock_event_with_user, mock_handler):
        # Setup
        middleware = UserMiddleware(mock_container)
        data = {}
        
        mock_user = Mock(spec=User)
        user_service = AsyncMock()
        user_service.handle_new_user.return_value = mock_user
        mock_container.get_user_service.return_value = user_service
        
        # Execute
        await middleware(mock_handler, mock_event_with_user, data)
        
        # Assert - verify user is correct type
        assert isinstance(data["user"], Mock)  # Mock of User
        assert data["user"] == mock_user