import pytest
from unittest.mock import Mock
from app.core.services.ai.prompt_builders.conversation_prompt_builder import ConversationPromptBuilder
from app.core.models.message import Message, MessageRole


class TestConversationPromptBuilder:
    @pytest.fixture
    def prompt_builder(self):
        return ConversationPromptBuilder()

    @pytest.fixture
    def sample_messages(self):
        messages = []
        
        # User message
        user_msg = Mock(spec=Message)
        user_msg.role = MessageRole.USER
        user_msg.content = "Hello, how are you?"
        messages.append(user_msg)
        
        # Assistant message
        assistant_msg = Mock(spec=Message)
        assistant_msg.role = MessageRole.ASSISTANT
        assistant_msg.content = "I'm doing well, thank you!"
        messages.append(assistant_msg)
        
        # Another user message
        user_msg2 = Mock(spec=Message)
        user_msg2.role = MessageRole.USER
        user_msg2.content = "What's the weather like?"
        messages.append(user_msg2)
        
        return messages

    def test_build_with_messages(self, prompt_builder, sample_messages):
        # Execute
        result = prompt_builder.build(sample_messages)
        
        # Assert
        expected_system = "You are a helpful assistant. Don't write yout message role in response."
        expected_messages = (
            "MessageRole.USER: Hello, how are you?\n"
            "MessageRole.ASSISTANT: I'm doing well, thank you!\n"
            "MessageRole.USER: What's the weather like?"
        )
        expected_full = expected_system + "\n\n" + expected_messages
        
        assert result == expected_full

    def test_build_with_empty_messages(self, prompt_builder):
        # Execute
        result = prompt_builder.build([])
        
        # Assert
        expected_system = "You are a helpful assistant. Don't write yout message role in response."
        expected_full = expected_system + "\n\n" + ""
        
        assert result == expected_full

    def test_build_with_single_message(self, prompt_builder):
        # Setup
        message = Mock(spec=Message)
        message.role = MessageRole.USER
        message.content = "Single message"
        
        # Execute
        result = prompt_builder.build([message])
        
        # Assert
        expected_system = "You are a helpful assistant. Don't write yout message role in response."
        expected_messages = "MessageRole.USER: Single message"
        expected_full = expected_system + "\n\n" + expected_messages
        
        assert result == expected_full

    def test_build_preserves_message_order(self, prompt_builder):
        # Setup - create messages in specific order
        messages = []
        for i in range(3):
            msg = Mock(spec=Message)
            msg.role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            msg.content = f"Message {i}"
            messages.append(msg)
        
        # Execute
        result = prompt_builder.build(messages)
        
        # Assert - check that messages appear in correct order
        assert "Message 0" in result
        assert "Message 1" in result
        assert "Message 2" in result
        assert result.index("Message 0") < result.index("Message 1")
        assert result.index("Message 1") < result.index("Message 2")

    def test_build_handles_long_messages(self, prompt_builder):
        # Setup
        long_content = "a" * 1000  # Very long message
        message = Mock(spec=Message)
        message.role = MessageRole.USER
        message.content = long_content
        
        # Execute
        result = prompt_builder.build([message])
        
        # Assert
        assert long_content in result
        assert len(result) > 1000

    def test_build_handles_special_characters(self, prompt_builder):
        # Setup
        special_content = "Message with\nnewlines and\ttabs and émojis 🎉"
        message = Mock(spec=Message)
        message.role = MessageRole.ASSISTANT
        message.content = special_content
        
        # Execute
        result = prompt_builder.build([message])
        
        # Assert
        assert special_content in result
        assert "🎉" in result

    def test_system_prompt_content(self, prompt_builder):
        # Execute
        result = prompt_builder.build([])
        
        # Assert - check system prompt content
        assert "You are a helpful assistant" in result
        assert "Don't write yout message role in response" in result

    def test_message_format(self, prompt_builder):
        # Setup
        message = Mock(spec=Message)
        message.role = MessageRole.USER
        message.content = "Test message"
        
        # Execute
        result = prompt_builder.build([message])
        
        # Assert - check format
        assert "MessageRole.USER: Test message" in result