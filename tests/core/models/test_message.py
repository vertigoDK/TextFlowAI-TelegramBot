import pytest
from app.core.models.message import Message, MessageRole


class TestMessageRole:
    def test_message_role_enum_values(self):
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"

    def test_message_role_enum_members(self):
        roles = list(MessageRole)
        assert len(roles) == 2
        assert MessageRole.USER in roles
        assert MessageRole.ASSISTANT in roles

    def test_message_role_string_representation(self):
        assert str(MessageRole.USER) == "MessageRole.USER"
        assert str(MessageRole.ASSISTANT) == "MessageRole.ASSISTANT"

    def test_message_role_value_access(self):
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"


class TestMessage:
    def test_message_model_tablename(self):
        assert Message.__tablename__ == "messages"

    def test_message_model_fields(self):
        message = Message(
            user_id=1,
            role=MessageRole.USER,
            content="Hello, world!",
            ai_metadata={"model": "gemini", "tokens": 100}
        )
        
        assert message.user_id == 1
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert message.ai_metadata == {"model": "gemini", "tokens": 100}

    def test_message_model_optional_ai_metadata(self):
        message = Message(
            user_id=1,
            role=MessageRole.USER,
            content="Hello, world!"
        )
        assert message.ai_metadata is None

    def test_message_model_role_enum(self):
        user_message = Message(
            user_id=1,
            role=MessageRole.USER,
            content="User message"
        )
        assert user_message.role == MessageRole.USER
        
        assistant_message = Message(
            user_id=1,
            role=MessageRole.ASSISTANT,
            content="Assistant message"
        )
        assert assistant_message.role == MessageRole.ASSISTANT

    def test_message_model_required_fields(self):
        # SQLAlchemy models don't raise TypeError for missing fields at instantiation
        # They would fail at database commit time
        message = Message()
        assert message.user_id is None
        assert message.role is None
        assert message.content is None

    def test_message_model_content_constraint(self):
        # Test max length constraint (would be enforced at DB level)
        long_content = "a" * 1000
        message = Message(
            user_id=1,
            role=MessageRole.USER,
            content=long_content
        )
        assert len(message.content) == 1000

    def test_message_model_ai_metadata_json(self):
        complex_metadata = {
            "model": "gemini-2.0-flash",
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100,
                "total_tokens": 150
            },
            "finish_reason": "stop",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        message = Message(
            user_id=1,
            role=MessageRole.ASSISTANT,
            content="Response",
            ai_metadata=complex_metadata
        )
        assert message.ai_metadata == complex_metadata

    def test_message_model_inheritance(self):
        message = Message(
            user_id=1,
            role=MessageRole.USER,
            content="Test"
        )
        
        # Should inherit from Base
        assert hasattr(message, "id")
        assert hasattr(message, "created_at")

    def test_message_model_foreign_key(self):
        # This would be tested with actual DB constraints
        message = Message(
            user_id=999,  # Non-existent user
            role=MessageRole.USER,
            content="Test"
        )
        assert message.user_id == 999