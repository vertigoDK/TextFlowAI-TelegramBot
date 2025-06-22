import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch
from aiogram.types import Message as TelegramMessage, User as TelegramUser
from app.bot.handlers.messages import handle_text_message
from app.core.models.user import User
from app.core.models.message import MessageRole
from app.core.services.container import Container


class TestMessagesHandler:
    @pytest_asyncio.fixture
    async def mock_telegram_message(self):
        """Mock Telegram message"""
        message = Mock(spec=TelegramMessage)
        message.text = "Hello, bot!"
        message.answer = AsyncMock()
        return message

    @pytest_asyncio.fixture
    async def mock_telegram_message_no_text(self):
        """Mock Telegram message without text"""
        message = Mock(spec=TelegramMessage)
        message.text = None
        message.answer = AsyncMock()
        return message

    @pytest_asyncio.fixture
    async def mock_user(self):
        """Mock user"""
        user = Mock(spec=User)
        user.id = 1
        user.telegram_id = 123456789
        user.first_name = "Test User"
        user.username = "test_user"
        return user

    @pytest_asyncio.fixture
    async def mock_container(self):
        """Mock container with services"""
        container = Mock(spec=Container)
        
        # Mock user service
        user_service = AsyncMock()
        user_service.can_make_request.return_value = True
        user_service.process_user_request.return_value = Mock()
        
        # Mock message service
        message_service = AsyncMock()
        message_service.create_message.return_value = Mock()
        message_service.get_conversation_context.return_value = []
        
        # Mock AI generator
        conversation_ai = AsyncMock()
        conversation_ai.agenerate.return_value = {
            "content": "AI response to your message",
            "model": "gemini-2.0-flash"
        }
        
        container.get_user_service.return_value = user_service
        container.get_message_service.return_value = message_service
        container.conversation_ai = conversation_ai
        
        return container

    @pytest.mark.asyncio
    async def test_handle_text_message_success(self, mock_telegram_message, mock_user, mock_container):
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert - verify service calls
        user_service = await mock_container.get_user_service()
        message_service = await mock_container.get_message_service()
        
        user_service.can_make_request.assert_called_once_with(mock_user.telegram_id)
        # Should be called twice - user message and AI response
        assert message_service.create_message.call_count == 2
        message_service.get_conversation_context.assert_called_once_with(
            telegram_id=mock_user.telegram_id
        )
        user_service.process_user_request.assert_called_once_with(
            telegram_id=mock_user.telegram_id,
            first_name=mock_user.first_name,
            username=mock_user.username
        )
        
        # Verify AI generation
        mock_container.conversation_ai.agenerate.assert_called_once()
        
        # Verify response sent
        mock_telegram_message.answer.assert_called_once_with("AI response to your message")

    @pytest.mark.asyncio
    async def test_handle_text_message_no_text(self, mock_telegram_message_no_text, mock_user, mock_container):
        # Execute
        await handle_text_message(mock_telegram_message_no_text, mock_user, mock_container)
        
        # Assert - should return early, no services called
        mock_container.get_user_service.assert_not_called()
        mock_container.get_message_service.assert_not_called()
        mock_telegram_message_no_text.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_text_message_rate_limited(self, mock_telegram_message, mock_user, mock_container):
        # Setup - user has reached limit
        user_service = AsyncMock()
        user_service.can_make_request.return_value = False
        mock_container.get_user_service.return_value = user_service
        
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert
        user_service.can_make_request.assert_called_once_with(mock_user.telegram_id)
        mock_telegram_message.answer.assert_called_once_with("You have reached your daily limit.")
        
        # Verify no further processing
        user_service.process_user_request.assert_not_called()
        mock_container.conversation_ai.agenerate.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_text_message_creates_user_message(self, mock_telegram_message, mock_user, mock_container):
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert
        message_service = await mock_container.get_message_service()
        message_service.create_message.assert_any_call(
            telegram_id=mock_user.telegram_id,
            role=MessageRole.USER,
            content="Hello, bot!"
        )

    @pytest.mark.asyncio
    async def test_handle_text_message_creates_ai_response(self, mock_telegram_message, mock_user, mock_container):
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert - verify AI response is saved
        message_service = await mock_container.get_message_service()
        
        # Should be called twice - once for user message, once for AI response
        assert message_service.create_message.call_count == 2
        
        # Check AI response call
        ai_response_call = message_service.create_message.call_args_list[1]
        assert ai_response_call[1]['telegram_id'] == mock_user.telegram_id
        assert ai_response_call[1]['role'] == MessageRole.ASSISTANT
        assert ai_response_call[1]['content'] == "AI response to your message"
        assert 'ai_metadata' in ai_response_call[1]

    @pytest.mark.asyncio
    async def test_handle_text_message_gets_conversation_context(self, mock_telegram_message, mock_user, mock_container):
        # Setup - mock context messages
        context_messages = [Mock(), Mock()]
        message_service = AsyncMock()
        message_service.create_message.return_value = Mock()
        message_service.get_conversation_context.return_value = context_messages
        mock_container.get_message_service.return_value = message_service
        
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert - context is retrieved and passed to AI
        message_service.get_conversation_context.assert_called_once_with(
            telegram_id=mock_user.telegram_id
        )
        mock_container.conversation_ai.agenerate.assert_called_once_with(context_messages)

    @pytest.mark.asyncio
    async def test_handle_text_message_processes_user_request(self, mock_telegram_message, mock_user, mock_container):
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert
        user_service = await mock_container.get_user_service()
        user_service.process_user_request.assert_called_once_with(
            telegram_id=mock_user.telegram_id,
            first_name=mock_user.first_name,
            username=mock_user.username
        )

    @pytest.mark.asyncio
    async def test_handle_text_message_uses_separate_services(self, mock_telegram_message, mock_user, mock_container):
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert - verify separate service instances are created
        assert mock_container.get_user_service.call_count == 1
        assert mock_container.get_message_service.call_count == 1

    @pytest.mark.asyncio
    async def test_handle_text_message_ai_metadata_preserved(self, mock_telegram_message, mock_user, mock_container):
        # Setup - AI returns metadata
        ai_response = {
            "content": "AI response",
            "model": "gemini-2.0-flash",
            "usage": {"tokens": 50}
        }
        mock_container.conversation_ai.agenerate.return_value = ai_response
        
        # Execute
        await handle_text_message(mock_telegram_message, mock_user, mock_container)
        
        # Assert - metadata is preserved in message creation
        message_service = await mock_container.get_message_service()
        ai_message_call = message_service.create_message.call_args_list[1]
        assert ai_message_call[1]['ai_metadata'] == ai_response

    @pytest.mark.asyncio
    async def test_handle_text_message_empty_text(self):
        # Setup
        message = Mock(spec=TelegramMessage)
        message.text = ""  # Empty text
        message.answer = AsyncMock()
        
        user = Mock(spec=User)
        container = Mock(spec=Container)
        
        user_service = AsyncMock()
        user_service.can_make_request.return_value = True
        container.get_user_service.return_value = user_service
        
        message_service = AsyncMock()
        container.get_message_service.return_value = message_service
        
        conversation_ai = AsyncMock()
        conversation_ai.agenerate.return_value = {"content": "response"}
        container.conversation_ai = conversation_ai
        
        # Execute
        await handle_text_message(message, user, container)
        
        # Assert - should process empty text normally
        container.get_user_service.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_text_message_whitespace_text(self):
        # Setup
        message = Mock(spec=TelegramMessage)
        message.text = "   \n\t   "  # Only whitespace
        message.answer = AsyncMock()
        
        user = Mock(spec=User)
        container = Mock(spec=Container)
        
        user_service = AsyncMock()
        user_service.can_make_request.return_value = True
        container.get_user_service.return_value = user_service
        
        message_service = AsyncMock()
        container.get_message_service.return_value = message_service
        
        conversation_ai = AsyncMock()
        conversation_ai.agenerate.return_value = {"content": "response"}
        container.conversation_ai = conversation_ai
        
        # Execute
        await handle_text_message(message, user, container)
        
        # Assert - whitespace text should be processed
        container.get_user_service.assert_called_once()
        user_service.can_make_request.assert_called_once()