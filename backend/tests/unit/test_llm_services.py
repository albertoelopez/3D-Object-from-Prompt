import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.llm.ollama import OllamaProvider
from app.services.llm.groq import GroqProvider


class TestOllamaProvider:
    @pytest.fixture
    def provider(self):
        return OllamaProvider()

    @pytest.mark.asyncio
    async def test_enhance_prompt_success(self, provider):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "A beautifully detailed red wooden chair with ornate carvings"
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            enhanced, model = await provider.enhance_prompt("a red chair")

            assert enhanced == "A beautifully detailed red wooden chair with ornate carvings"
            assert model == "llama3.2"

    @pytest.mark.asyncio
    async def test_enhance_prompt_empty_response(self, provider):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": ""}
        mock_response.raise_for_status = MagicMock()

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            enhanced, model = await provider.enhance_prompt("a red chair")

            assert enhanced == "a red chair"

    @pytest.mark.asyncio
    async def test_is_available_success(self, provider):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await provider.is_available()

            assert result is True

    @pytest.mark.asyncio
    async def test_is_available_failure(self, provider):
        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection refused")

            result = await provider.is_available()

            assert result is False


class TestGroqProvider:
    @pytest.fixture
    def provider(self):
        with patch.object(GroqProvider, '__init__', lambda self: None):
            p = GroqProvider()
            p.api_key = "test-api-key"
            p.default_model = "llama-3.3-70b-versatile"
            p.base_url = "https://api.groq.com/openai/v1"
            return p

    @pytest.mark.asyncio
    async def test_enhance_prompt_success(self, provider):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "A detailed vintage red armchair"}}
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            enhanced, model = await provider.enhance_prompt("a red chair")

            assert enhanced == "A detailed vintage red armchair"
            assert model == "llama-3.3-70b-versatile"

    @pytest.mark.asyncio
    async def test_enhance_prompt_no_api_key(self):
        with patch.object(GroqProvider, '__init__', lambda self: None):
            p = GroqProvider()
            p.api_key = None
            p.default_model = "llama-3.3-70b-versatile"
            p.base_url = "https://api.groq.com/openai/v1"

            with pytest.raises(ValueError, match="Groq API key not configured"):
                await p.enhance_prompt("test")

    @pytest.mark.asyncio
    async def test_is_available_with_key(self, provider):
        result = await provider.is_available()
        assert result is True

    @pytest.mark.asyncio
    async def test_is_available_without_key(self):
        with patch.object(GroqProvider, '__init__', lambda self: None):
            p = GroqProvider()
            p.api_key = None

            result = await p.is_available()
            assert result is False
