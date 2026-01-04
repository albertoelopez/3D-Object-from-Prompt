import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import redis.asyncio as aioredis

from app.main import app
from app.core.redis import init_redis, close_redis


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_redis():
    mock = AsyncMock(spec=aioredis.Redis)
    mock.hset = AsyncMock(return_value=True)
    mock.hgetall = AsyncMock(return_value={})
    mock.rpush = AsyncMock(return_value=1)
    mock.llen = AsyncMock(return_value=0)
    mock.lrange = AsyncMock(return_value=[])
    mock.expire = AsyncMock(return_value=True)
    mock.ping = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def sample_job():
    return {
        "job_id": "test-job-123",
        "job_type": "text_to_3d",
        "status": "queued",
        "input_data": {
            "type": "text",
            "prompt": "a red chair",
            "enhance_prompt": False,
            "llm_provider": "ollama"
        },
        "parameters": {
            "seed": 42,
            "resolution": "medium"
        },
        "created_at": "2026-01-03T12:00:00Z",
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
        "progress": 0,
        "stage": "queued",
        "stage_progress": 0
    }
