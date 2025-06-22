import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
from app.core.services.message_service import MessageService
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.message_repository import MessageRepository
from app.core.models.user import User
from app.core.models.message import Message, MessageRole
from app.core.exceptions.user import UserNotFound, InvalidTelegramID
from app.core.exceptions.message import InvalidMessageData
from app.core.exceptions.base import TextFlowException
from sqlalchemy.exc import SQLAlchemyError


class TestMessageService:
    @pytest_asyncio.fixture
    async def mock_user_repository(self):
        """Mock UserRepository for testing"""
        return AsyncMock(spec=UserRepository)

    @pytest_asyncio.fixture
    async def mock_message_repository(self):
        """Mock MessageRepository for testing"""
        return AsyncMock(spec=MessageRepository)

    @pytest_asyncio.fixture
    async def message_service(self, mock_user_repository, mock_message_repository):
        """Create MessageService with mocked repositories"""
        return MessageService(mock_user_repository, mock_message_repository)

    @pytest_asyncio.fixture
    async def sample_user(self):
        """Sample user for testing"""
        user = Mock(spec=User)
        user.id = 1
        user.telegram_id = 123456789
        user.first_name = "Test User"
        user.username = "test_user"
        return user

    @pytest_asyncio.fixture
    async def sample_message(self):
        """Sample message for testing"""
        message = Mock(spec=Message)
        message.id = 1
        message.user_id = 1
        message.role = MessageRole.USER
        message.content = "Test message"
        message.ai_metadata = None
        return message

    @pytest.mark.asyncio
    async def test_create_message_success(self, message_service, mock_user_repository, mock_message_repository, sample_user, sample_message):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.create_message.return_value = sample_message
        
        # Execute
        result = await message_service.create_message(
            telegram_id=123456789,
            role=MessageRole.USER,
            content="Test message",
            ai_metadata={"model": "gemini"}
        )
        
        # Assert
        assert result == sample_message
        mock_user_repository.get_by_telegram_id.assert_called_once_with(telegram_id=123456789)
        mock_message_repository.create_message.assert_called_once_with(
            user_id=1,
            role=MessageRole.USER,
            content="Test message",
            ai_metadata={"model": "gemini"}
        )

    @pytest.mark.asyncio
    async def test_create_message_without_metadata(self, message_service, mock_user_repository, mock_message_repository, sample_user, sample_message):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.create_message.return_value = sample_message
        
        # Execute
        result = await message_service.create_message(
            telegram_id=123456789,
            role=MessageRole.ASSISTANT,
            content="AI response"
        )
        
        # Assert
        assert result == sample_message
        mock_message_repository.create_message.assert_called_once_with(
            user_id=1,
            role=MessageRole.ASSISTANT,
            content="AI response",
            ai_metadata=None
        )

    @pytest.mark.asyncio
    async def test_create_message_user_not_found(self, message_service, mock_user_repository, mock_message_repository):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(UserNotFound) as exc_info:
            await message_service.create_message(
                telegram_id=123456789,
                role=MessageRole.USER,
                content="Test message"
            )
        
        assert exc_info.value.telegram_id == 123456789
        mock_message_repository.create_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_message_invalid_telegram_id(self, message_service):
        # Execute & Assert
        with pytest.raises(InvalidTelegramID):
            await message_service.create_message(
                telegram_id=0,
                role=MessageRole.USER,
                content="Test message"
            )

    @pytest.mark.asyncio
    async def test_create_message_empty_content(self, message_service):
        # Execute & Assert
        with pytest.raises(InvalidMessageData, match="Message content cannot be empty"):
            await message_service.create_message(
                telegram_id=123456789,
                role=MessageRole.USER,
                content="   "  # Empty after strip
            )

    @pytest.mark.asyncio
    async def test_create_message_content_too_long(self, message_service):
        # Execute & Assert
        long_content = "a" * 4097  # Exceeds max length
        with pytest.raises(InvalidMessageData, match="Message content too long"):
            await message_service.create_message(
                telegram_id=123456789,
                role=MessageRole.USER,
                content=long_content
            )

    @pytest.mark.asyncio
    async def test_create_message_sqlalchemy_error(self, message_service, mock_user_repository, mock_message_repository, sample_user):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.create_message.side_effect = SQLAlchemyError("DB Error")
        
        # Execute & Assert
        with pytest.raises(TextFlowException, match="Failed to create message"):
            await message_service.create_message(
                telegram_id=123456789,
                role=MessageRole.USER,
                content="Test message"
            )

    @pytest.mark.asyncio
    async def test_get_conversation_context_success(self, message_service, mock_user_repository, mock_message_repository, sample_user):
        # Setup
        mock_messages = [Mock(spec=Message), Mock(spec=Message)]
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.get_recent_context.return_value = mock_messages
        
        # Execute
        result = await message_service.get_conversation_context(
            telegram_id=123456789,
            context_limit=5
        )
        
        # Assert
        assert result == mock_messages
        mock_user_repository.get_by_telegram_id.assert_called_once_with(telegram_id=123456789)
        mock_message_repository.get_recent_context.assert_called_once_with(
            user_id=1,
            limit=5
        )

    @pytest.mark.asyncio
    async def test_get_conversation_context_default_limit(self, message_service, mock_user_repository, mock_message_repository, sample_user):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.get_recent_context.return_value = []
        
        # Execute
        await message_service.get_conversation_context(telegram_id=123456789)
        
        # Assert
        mock_message_repository.get_recent_context.assert_called_once_with(
            user_id=1,
            limit=10  # Default value
        )

    @pytest.mark.asyncio
    async def test_get_conversation_context_user_not_found(self, message_service, mock_user_repository, mock_message_repository):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(UserNotFound):
            await message_service.get_conversation_context(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_get_conversation_context_invalid_telegram_id(self, message_service):
        # Execute & Assert
        with pytest.raises(InvalidTelegramID):
            await message_service.get_conversation_context(telegram_id=0)

    @pytest.mark.asyncio
    async def test_get_conversation_context_sqlalchemy_error(self, message_service, mock_user_repository, sample_user):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_user_repository.get_by_telegram_id.side_effect = SQLAlchemyError("DB Error")
        
        # Execute & Assert
        with pytest.raises(TextFlowException, match="Failed to get conversation context"):
            await message_service.get_conversation_context(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_get_user_messages_success(self, message_service, mock_user_repository, mock_message_repository, sample_user):
        # Setup
        mock_messages = [Mock(spec=Message), Mock(spec=Message)]
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.get_user_messages.return_value = mock_messages
        
        # Execute
        result = await message_service.get_user_messages(
            telegram_id=123456789,
            limit=50,
            offset=10
        )
        
        # Assert
        assert result == mock_messages
        mock_user_repository.get_by_telegram_id.assert_called_once_with(telegram_id=123456789)
        mock_message_repository.get_user_messages.assert_called_once_with(
            user_id=1,
            limit=50,
            offset=10
        )

    @pytest.mark.asyncio
    async def test_get_user_messages_default_params(self, message_service, mock_user_repository, mock_message_repository, sample_user):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.get_user_messages.return_value = []
        
        # Execute
        await message_service.get_user_messages(telegram_id=123456789)
        
        # Assert
        mock_message_repository.get_user_messages.assert_called_once_with(
            user_id=1,
            limit=20,  # Default
            offset=0   # Default
        )

    @pytest.mark.asyncio
    async def test_get_user_messages_user_not_found(self, message_service, mock_user_repository):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(UserNotFound):
            await message_service.get_user_messages(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_get_user_messages_invalid_telegram_id(self, message_service):
        # Execute & Assert
        with pytest.raises(InvalidTelegramID):
            await message_service.get_user_messages(telegram_id=0)

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_all_users(self, message_service, mock_message_repository):
        # Setup
        mock_message_repository.delete_old_messages.return_value = 10
        
        # Execute
        result = await message_service.cleanup_old_messages(days_old=30)
        
        # Assert
        assert result == 10
        mock_message_repository.delete_old_messages.assert_called_once_with(
            days_old=30,
            user_id=None
        )

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_specific_user(self, message_service, mock_user_repository, mock_message_repository, sample_user):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = sample_user
        mock_message_repository.delete_old_messages.return_value = 5
        
        # Execute
        result = await message_service.cleanup_old_messages(
            days_old=7,
            telegram_id=123456789
        )
        
        # Assert
        assert result == 5
        mock_user_repository.get_by_telegram_id.assert_called_once_with(telegram_id=123456789)
        mock_message_repository.delete_old_messages.assert_called_once_with(
            days_old=7,
            user_id=1
        )

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_user_not_found(self, message_service, mock_user_repository):
        # Setup
        mock_user_repository.get_by_telegram_id.return_value = None
        
        # Execute & Assert
        with pytest.raises(UserNotFound):
            await message_service.cleanup_old_messages(
                days_old=30,
                telegram_id=123456789
            )

    @pytest.mark.asyncio
    async def test_cleanup_old_messages_sqlalchemy_error(self, message_service, mock_message_repository):
        # Setup
        mock_message_repository.delete_old_messages.side_effect = SQLAlchemyError("DB Error")
        
        # Execute & Assert
        with pytest.raises(TextFlowException, match="Failed to cleanup old messages"):
            await message_service.cleanup_old_messages(days_old=30)

    @pytest.mark.asyncio
    async def test_validate_message_input_valid(self, message_service):
        # This should not raise any exception
        message_service._validate_message_input(
            telegram_id=123456789,
            content="Valid message content"
        )

    @pytest.mark.asyncio
    async def test_validate_message_input_strips_whitespace(self, message_service):
        # This should not raise any exception (content gets stripped)
        message_service._validate_message_input(
            telegram_id=123456789,
            content="  Valid content with spaces  "
        )

    @pytest.mark.asyncio
    async def test_message_service_dependencies(self, mock_user_repository, mock_message_repository):
        # Execute
        service = MessageService(mock_user_repository, mock_message_repository)
        
        # Assert
        assert service.user_repository == mock_user_repository
        assert service.message_repository == mock_message_repository