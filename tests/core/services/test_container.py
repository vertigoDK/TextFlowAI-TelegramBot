import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
from app.core.services.container import Container
from app.core.services.user_service import UserService
from app.core.services.message_service import MessageService
from app.core.services.ai.generator import AIGenerator
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.message_repository import MessageRepository


class TestContainer:
    @pytest.mark.asyncio
    async def test_container_initialization(self):
        # Execute
        container = Container()
        
        # Assert - conversation_ai should be available immediately
        assert hasattr(container, 'conversation_ai')
        assert isinstance(container.conversation_ai, AIGenerator)

    @pytest.mark.asyncio
    async def test_get_user_service_creates_new_instance(self):
        # Setup
        container = Container()
        
        # Execute
        with patch('app.core.services.container.SessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value = mock_session
            
            user_service = await container.get_user_service()
        
        # Assert
        assert isinstance(user_service, UserService)
        assert isinstance(user_service.user_repository, UserRepository)
        assert user_service.user_repository.session == mock_session

    @pytest.mark.asyncio
    async def test_get_user_service_creates_separate_sessions(self):
        # Setup
        container = Container()
        
        # Execute - call get_user_service twice
        with patch('app.core.services.container.SessionLocal') as mock_session_local:
            mock_session1 = AsyncMock()
            mock_session2 = AsyncMock()
            mock_session_local.side_effect = [mock_session1, mock_session2]
            
            user_service1 = await container.get_user_service()
            user_service2 = await container.get_user_service()
        
        # Assert - should create separate sessions
        assert user_service1.user_repository.session == mock_session1
        assert user_service2.user_repository.session == mock_session2
        assert user_service1.user_repository.session != user_service2.user_repository.session

    @pytest.mark.asyncio
    async def test_get_message_service_creates_new_instance(self):
        # Setup
        container = Container()
        
        # Execute
        with patch('app.core.services.container.SessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value = mock_session
            
            message_service = await container.get_message_service()
        
        # Assert
        assert isinstance(message_service, MessageService)
        assert isinstance(message_service.user_repository, UserRepository)
        assert isinstance(message_service.message_repository, MessageRepository)
        assert message_service.user_repository.session == mock_session
        assert message_service.message_repository.session == mock_session

    @pytest.mark.asyncio
    async def test_get_message_service_creates_separate_sessions(self):
        # Setup
        container = Container()
        
        # Execute - call get_message_service twice
        with patch('app.core.services.container.SessionLocal') as mock_session_local:
            mock_session1 = AsyncMock()
            mock_session2 = AsyncMock()
            mock_session_local.side_effect = [mock_session1, mock_session2]
            
            message_service1 = await container.get_message_service()
            message_service2 = await container.get_message_service()
        
        # Assert - should create separate sessions
        assert message_service1.user_repository.session == mock_session1
        assert message_service2.user_repository.session == mock_session2
        assert message_service1.user_repository.session != message_service2.user_repository.session

    @pytest.mark.asyncio
    async def test_conversation_ai_property_same_instance(self):
        # Setup
        container = Container()
        
        # Execute
        ai1 = container.conversation_ai
        ai2 = container.conversation_ai
        
        # Assert - should return the same instance (singleton pattern)
        assert ai1 is ai2
        assert isinstance(ai1, AIGenerator)

    @pytest.mark.asyncio
    async def test_get_user_service_different_from_message_service_repos(self):
        # Setup
        container = Container()
        
        # Execute
        with patch('app.core.services.container.SessionLocal') as mock_session_local:
            mock_session1 = AsyncMock()
            mock_session2 = AsyncMock()
            mock_session_local.side_effect = [mock_session1, mock_session2]
            
            user_service = await container.get_user_service()
            message_service = await container.get_message_service()
        
        # Assert - each service should have its own session
        assert user_service.user_repository.session == mock_session1
        assert message_service.user_repository.session == mock_session2
        # They should be different repository instances even though same type
        assert user_service.user_repository is not message_service.user_repository

    @pytest.mark.asyncio
    async def test_message_service_has_both_repositories(self):
        # Setup
        container = Container()
        
        # Execute
        with patch('app.core.services.container.SessionLocal') as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value = mock_session
            
            message_service = await container.get_message_service()
        
        # Assert - MessageService should have both user and message repositories
        assert hasattr(message_service, 'user_repository')
        assert hasattr(message_service, 'message_repository')
        assert isinstance(message_service.user_repository, UserRepository)
        assert isinstance(message_service.message_repository, MessageRepository)
        # Both repositories should use the same session
        assert message_service.user_repository.session == mock_session
        assert message_service.message_repository.session == mock_session

    @pytest.mark.asyncio
    async def test_container_per_request_pattern(self):
        """Test that the container properly implements per-request session pattern"""
        # Setup
        container = Container()
        
        # Execute - simulate multiple requests
        services = []
        with patch('app.core.services.container.SessionLocal') as mock_session_local:
            # Create 3 different sessions for 3 requests
            sessions = [AsyncMock() for _ in range(3)]
            mock_session_local.side_effect = sessions
            
            # Simulate 3 different requests
            for _ in range(3):
                user_service = await container.get_user_service()
                services.append(user_service)
        
        # Assert - each service should have a different session
        for i in range(3):
            assert services[i].user_repository.session == sessions[i]
        
        # All sessions should be different
        session_ids = [id(service.user_repository.session) for service in services]
        assert len(set(session_ids)) == 3  # All unique

    @pytest.mark.asyncio
    async def test_container_ai_components_initialization(self):
        """Test that AI components are properly initialized"""
        # Execute
        container = Container()
        
        # Assert
        ai_generator = container.conversation_ai
        assert isinstance(ai_generator, AIGenerator)
        
        # AI generator should have provider and prompt_builder
        assert hasattr(ai_generator, 'provider')
        assert hasattr(ai_generator, 'prompt_builder')
        
        # Provider should be Google provider
        from app.core.services.ai.providers.google_provider import GoogleProvider
        assert isinstance(ai_generator.provider, GoogleProvider)
        
        # Prompt builder should be conversation prompt builder
        from app.core.services.ai.prompt_builders.conversation_prompt_builder import ConversationPromptBuilder
        assert isinstance(ai_generator.prompt_builder, ConversationPromptBuilder)