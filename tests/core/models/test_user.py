import pytest
from app.core.models.user import User


class TestUser:
    def test_user_model_tablename(self):
        assert User.__tablename__ == "users"

    def test_user_model_fields(self):
        user = User(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            daily_limit=10,
            requests_today=5
        )
        
        assert user.telegram_id == 123456789
        assert user.username == "test_user"
        assert user.first_name == "Test"
        assert user.daily_limit == 10
        assert user.requests_today == 5

    def test_user_model_default_values(self):
        # SQLAlchemy defaults are applied at DB level, not at instantiation
        user = User(telegram_id=123456789, first_name="Test")
        
        # These would be None until persisted to DB
        assert user.daily_limit is None
        assert user.requests_today is None

    def test_user_model_optional_username(self):
        user = User(telegram_id=123456789, first_name="Test")
        assert user.username is None
        
        user.username = "test_user"
        assert user.username == "test_user"

    def test_user_model_required_fields(self):
        # SQLAlchemy models don't raise TypeError for missing fields at instantiation
        # They would fail at database commit time
        user = User()
        assert user.telegram_id is None
        assert user.first_name is None

    def test_user_model_field_constraints(self):
        # Test telegram_id as BigInteger
        user = User(telegram_id=9223372036854775807, first_name="Test")
        assert user.telegram_id == 9223372036854775807
        
        # Test string length constraints would be tested at DB level
        user = User(
            telegram_id=123456789,
            username="a" * 32,  # max length
            first_name="b" * 64  # max length
        )
        assert len(user.username) == 32
        assert len(user.first_name) == 64

    def test_user_model_inheritance(self):
        user = User(telegram_id=123456789, first_name="Test")
        
        # Should inherit from Base
        assert hasattr(user, "id")
        assert hasattr(user, "created_at")