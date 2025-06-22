import pytest
from datetime import datetime

from app.core.models.base import Base


class TestBase:
    def test_base_model_has_id_field(self):
        class TestModel1(Base):
            __tablename__ = "test_model1"
        
        assert hasattr(TestModel1, "id")
        assert TestModel1.__table__.columns["id"].primary_key

    def test_base_model_has_created_at_field(self):
        class TestModel2(Base):
            __tablename__ = "test_model2"
        
        assert hasattr(TestModel2, "created_at")
        created_at_column = TestModel2.__table__.columns["created_at"]
        assert created_at_column.server_default is not None

    def test_base_model_metadata_naming_convention(self):
        assert "pk" in Base.metadata.naming_convention
        assert Base.metadata.naming_convention["pk"] == "pk_%(table_name)s"

    def test_base_model_instance_creation(self):
        class TestModel3(Base):
            __tablename__ = "test_model3"
        
        instance = TestModel3()
        assert instance.id is None
        assert instance.created_at is None