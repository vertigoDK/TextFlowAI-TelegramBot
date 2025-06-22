import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch
from app.core.services.ai.providers.google_provider import GoogleProvider


class TestGoogleProvider:
    @pytest.mark.asyncio
    async def test_google_provider_initialization(self):
        # Setup
        with patch('app.core.services.ai.providers.google_provider.ChatGoogleGenerativeAI') as mock_chat_ai:
            with patch('app.core.services.ai.providers.google_provider.settings') as mock_settings:
                mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "test-api-key"
                
                # Execute
                provider = GoogleProvider("gemini-2.0-flash")
                
                # Assert
                assert provider.model_name == "gemini-2.0-flash"
                mock_chat_ai.assert_called_once_with(
                    api_key="test-api-key",
                    model="gemini-2.0-flash"
                )

    @pytest.mark.asyncio
    async def test_agenerate_success(self):
        # Setup
        with patch('app.core.services.ai.providers.google_provider.ChatGoogleGenerativeAI') as mock_chat_ai:
            with patch('app.core.services.ai.providers.google_provider.settings') as mock_settings:
                mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "test-api-key"
                
                # Mock response
                mock_response = Mock()
                mock_response.content = "AI generated response"
                mock_response.response_metadata = {
                    "token_usage": {"total_tokens": 100}
                }
                
                mock_llm = AsyncMock()
                mock_llm.ainvoke.return_value = mock_response
                mock_chat_ai.return_value = mock_llm
                
                provider = GoogleProvider("gemini-2.0-flash")
                
                # Execute
                result = await provider.agenerate("Test prompt")
                
                # Assert
                assert result == {
                    "content": "AI generated response",
                    "model": "gemini-2.0-flash",
                    "usage": {"token_usage": {"total_tokens": 100}}
                }
                mock_llm.ainvoke.assert_called_once_with("Test prompt")

    @pytest.mark.asyncio
    async def test_agenerate_with_exception(self):
        # Setup
        with patch('app.core.services.ai.providers.google_provider.ChatGoogleGenerativeAI') as mock_chat_ai:
            with patch('app.core.services.ai.providers.google_provider.settings') as mock_settings:
                mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "test-api-key"
                
                mock_llm = AsyncMock()
                mock_llm.ainvoke.side_effect = Exception("API Error")
                mock_chat_ai.return_value = mock_llm
                
                provider = GoogleProvider("gemini-2.0-flash")
                
                # Execute & Assert
                with pytest.raises(Exception, match="API Error"):
                    await provider.agenerate("Test prompt")

    @pytest.mark.asyncio
    async def test_agenerate_empty_prompt(self):
        # Setup
        with patch('app.core.services.ai.providers.google_provider.ChatGoogleGenerativeAI') as mock_chat_ai:
            with patch('app.core.services.ai.providers.google_provider.settings') as mock_settings:
                mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "test-api-key"
                
                mock_response = Mock()
                mock_response.content = "Default response"
                mock_response.response_metadata = {}
                
                mock_llm = AsyncMock()
                mock_llm.ainvoke.return_value = mock_response
                mock_chat_ai.return_value = mock_llm
                
                provider = GoogleProvider("gemini-2.0-flash")
                
                # Execute
                result = await provider.agenerate("")
                
                # Assert
                assert result["content"] == "Default response"
                mock_llm.ainvoke.assert_called_once_with("")

    @pytest.mark.asyncio
    async def test_model_name_stored_correctly(self):
        # Setup
        with patch('app.core.services.ai.providers.google_provider.ChatGoogleGenerativeAI'):
            with patch('app.core.services.ai.providers.google_provider.settings') as mock_settings:
                mock_settings.GOOGLE_API_KEY.get_secret_value.return_value = "test-api-key"
                
                # Execute
                provider = GoogleProvider("gemini-2.0-flash")
                
                # Assert
                assert provider.model_name == "gemini-2.0-flash"