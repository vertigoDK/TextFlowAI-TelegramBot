import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
from app.core.services.ai.generator import AIGenerator
from app.core.models.message import Message, MessageRole


class TestAIGenerator:
    @pytest_asyncio.fixture
    async def mock_provider(self):
        """Mock provider for testing"""
        provider = AsyncMock()
        provider.agenerate.return_value = {
            "content": "AI response",
            "model": "test-model",
            "usage": {"tokens": 100}
        }
        return provider

    @pytest_asyncio.fixture
    async def mock_prompt_builder(self):
        """Mock prompt builder for testing"""
        builder = Mock()
        builder.build.return_value = "Built prompt from messages"
        return builder

    @pytest_asyncio.fixture
    async def ai_generator(self, mock_provider, mock_prompt_builder):
        """Create AIGenerator with mocked dependencies"""
        return AIGenerator(mock_provider, mock_prompt_builder)

    @pytest_asyncio.fixture
    async def sample_messages(self):
        """Sample messages for testing"""
        messages = []
        
        user_msg = Mock(spec=Message)
        user_msg.role = MessageRole.USER
        user_msg.content = "Hello"
        messages.append(user_msg)
        
        assistant_msg = Mock(spec=Message)
        assistant_msg.role = MessageRole.ASSISTANT
        assistant_msg.content = "Hi there!"
        messages.append(assistant_msg)
        
        return messages

    @pytest.mark.asyncio
    async def test_ai_generator_initialization(self, mock_provider, mock_prompt_builder):
        # Execute
        generator = AIGenerator(mock_provider, mock_prompt_builder)
        
        # Assert
        assert generator.provider == mock_provider
        assert generator.prompt_builder == mock_prompt_builder

    @pytest.mark.asyncio
    async def test_agenerate_success(self, ai_generator, mock_provider, mock_prompt_builder, sample_messages):
        # Execute
        result = await ai_generator.agenerate(sample_messages)
        
        # Assert
        assert result == {
            "content": "AI response",
            "model": "test-model",
            "usage": {"tokens": 100}
        }
        
        # Verify interactions
        mock_prompt_builder.build.assert_called_once_with(sample_messages)
        mock_provider.agenerate.assert_called_once_with("Built prompt from messages")

    @pytest.mark.asyncio
    async def test_agenerate_with_empty_messages(self, ai_generator, mock_provider, mock_prompt_builder):
        # Execute
        result = await ai_generator.agenerate([])
        
        # Assert
        assert result == {
            "content": "AI response",
            "model": "test-model",
            "usage": {"tokens": 100}
        }
        
        # Verify interactions
        mock_prompt_builder.build.assert_called_once_with([])
        mock_provider.agenerate.assert_called_once_with("Built prompt from messages")

    @pytest.mark.asyncio
    async def test_agenerate_provider_exception(self, ai_generator, mock_provider, mock_prompt_builder, sample_messages):
        # Setup
        mock_provider.agenerate.side_effect = Exception("Provider error")
        
        # Execute & Assert
        with pytest.raises(Exception, match="Provider error"):
            await ai_generator.agenerate(sample_messages)
        
        # Verify prompt builder was still called
        mock_prompt_builder.build.assert_called_once_with(sample_messages)

    @pytest.mark.asyncio
    async def test_agenerate_prompt_builder_exception(self, ai_generator, mock_provider, mock_prompt_builder, sample_messages):
        # Setup
        mock_prompt_builder.build.side_effect = Exception("Prompt builder error")
        
        # Execute & Assert
        with pytest.raises(Exception, match="Prompt builder error"):
            await ai_generator.agenerate(sample_messages)
        
        # Verify provider was not called
        mock_provider.agenerate.assert_not_called()

    @pytest.mark.asyncio
    async def test_agenerate_different_response_format(self, ai_generator, mock_provider, mock_prompt_builder, sample_messages):
        # Setup - different response format
        mock_provider.agenerate.return_value = {
            "content": "Different response",
            "model": "another-model",
            "usage": {"prompt_tokens": 50, "completion_tokens": 75},
            "finish_reason": "stop"
        }
        
        # Execute
        result = await ai_generator.agenerate(sample_messages)
        
        # Assert
        assert result["content"] == "Different response"
        assert result["model"] == "another-model"
        assert result["usage"]["prompt_tokens"] == 50
        assert result["finish_reason"] == "stop"

    @pytest.mark.asyncio
    async def test_agenerate_with_single_message(self, ai_generator, mock_provider, mock_prompt_builder):
        # Setup
        single_message = Mock(spec=Message)
        single_message.role = MessageRole.USER
        single_message.content = "Single message"
        
        # Execute
        result = await ai_generator.agenerate([single_message])
        
        # Assert
        assert result == {
            "content": "AI response",
            "model": "test-model",
            "usage": {"tokens": 100}
        }
        
        # Verify correct message was passed
        mock_prompt_builder.build.assert_called_once_with([single_message])

    @pytest.mark.asyncio
    async def test_agenerate_preserves_message_order(self, ai_generator, mock_provider, mock_prompt_builder):
        # Setup - multiple messages in specific order
        messages = []
        for i in range(5):
            msg = Mock(spec=Message)
            msg.role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            msg.content = f"Message {i}"
            messages.append(msg)
        
        # Execute
        await ai_generator.agenerate(messages)
        
        # Assert - verify exact message list was passed to prompt builder
        mock_prompt_builder.build.assert_called_once_with(messages)

    @pytest.mark.asyncio
    async def test_agenerate_return_type(self, ai_generator, sample_messages):
        # Execute
        result = await ai_generator.agenerate(sample_messages)
        
        # Assert - verify return type is dict
        assert isinstance(result, dict)
        assert "content" in result
        assert "model" in result
        assert "usage" in result