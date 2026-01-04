import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_queue():
    mock = MagicMock()
    mock.enqueue = AsyncMock(return_value="test-job-123")
    mock.get_job = AsyncMock(return_value={
        "job_id": "test-job-123",
        "status": "queued",
        "progress": 0,
        "stage": "queued",
        "stage_progress": 0,
        "created_at": "2026-01-03T12:00:00Z",
        "started_at": None,
        "completed_at": None,
        "input_data": {"type": "text", "prompt": "test"},
        "parameters": {"seed": 42},
        "result": None,
        "error": None
    })
    mock.get_queue_size = AsyncMock(return_value=5)
    return mock


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    return mock


class TestHealthEndpoint:
    def test_liveness(self, client):
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_readiness_redis_down(self, client):
        with patch('app.api.v1.endpoints.health.check_redis_health', new_callable=AsyncMock) as mock:
            mock.return_value = False

            response = client.get("/api/v1/health/ready")

            assert response.status_code == 200
            assert response.json()["status"] == "not_ready"


class TestGenerationEndpoints:
    def test_text_to_3d_success(self, client, mock_queue, mock_redis):
        with patch('app.api.v1.endpoints.generate.get_queue', return_value=mock_queue):
            with patch('app.core.redis.get_redis', return_value=mock_redis):
                response = client.post(
                    "/api/v1/generate/text-to-3d",
                    json={
                        "prompt": "a red chair",
                        "enhance_prompt": False,
                        "resolution": "medium"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert "job_id" in data
                assert data["status"] == "queued"

    def test_text_to_3d_empty_prompt(self, client):
        response = client.post(
            "/api/v1/generate/text-to-3d",
            json={"prompt": ""}
        )

        assert response.status_code == 422

    def test_image_to_3d_invalid_file_type(self, client, mock_queue, mock_redis):
        with patch('app.api.v1.endpoints.generate.get_queue', return_value=mock_queue):
            with patch('app.core.redis.get_redis', return_value=mock_redis):
                response = client.post(
                    "/api/v1/generate/image-to-3d",
                    files={"file": ("test.txt", b"not an image", "text/plain")}
                )

                assert response.status_code == 400


class TestJobEndpoints:
    def test_get_job_success(self, client, mock_queue, mock_redis):
        with patch('app.api.v1.endpoints.jobs.get_queue', return_value=mock_queue):
            with patch('app.core.redis.get_redis', return_value=mock_redis):
                response = client.get("/api/v1/jobs/test-job-123")

                assert response.status_code == 200
                data = response.json()
                assert data["job_id"] == "test-job-123"

    def test_get_job_not_found(self, client, mock_queue, mock_redis):
        mock_queue.get_job = AsyncMock(return_value=None)

        with patch('app.api.v1.endpoints.jobs.get_queue', return_value=mock_queue):
            with patch('app.core.redis.get_redis', return_value=mock_redis):
                response = client.get("/api/v1/jobs/nonexistent")

                assert response.status_code == 404

    def test_cancel_job_success(self, client, mock_queue, mock_redis):
        mock_queue.cancel_job = AsyncMock(return_value=True)

        with patch('app.api.v1.endpoints.jobs.get_queue', return_value=mock_queue):
            with patch('app.core.redis.get_redis', return_value=mock_redis):
                response = client.delete("/api/v1/jobs/test-job-123")

                assert response.status_code == 200


class TestPromptEndpoints:
    def test_enhance_prompt_success(self, client):
        with patch('app.api.v1.endpoints.prompts.ollama_provider') as mock_ollama:
            mock_ollama.enhance_prompt = AsyncMock(
                return_value=("A detailed red wooden chair", "llama3.2")
            )

            response = client.post(
                "/api/v1/prompts/enhance",
                json={"prompt": "a red chair", "provider": "ollama"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["original_prompt"] == "a red chair"
            assert "enhanced_prompt" in data
