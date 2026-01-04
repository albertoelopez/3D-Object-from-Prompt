import pytest
from unittest.mock import AsyncMock, patch
import json

from app.core.queue import JobQueue


@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.hset = AsyncMock(return_value=True)
    mock.rpush = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    mock.llen = AsyncMock(return_value=5)
    mock.lrange = AsyncMock(return_value=[b"job-1", b"job-2"])
    mock.lrem = AsyncMock(return_value=1)
    return mock


@pytest.fixture
def queue(mock_redis):
    return JobQueue(mock_redis)


@pytest.mark.asyncio
async def test_enqueue_job(queue, mock_redis):
    job_id = await queue.enqueue(
        job_type="text_to_3d",
        input_data={"prompt": "test"},
        parameters={"seed": 42}
    )

    assert job_id is not None
    assert len(job_id) == 36
    mock_redis.hset.assert_called_once()
    mock_redis.rpush.assert_called_once()
    mock_redis.expire.assert_called_once()


@pytest.mark.asyncio
async def test_get_job_not_found(queue, mock_redis):
    mock_redis.hgetall = AsyncMock(return_value={})

    job = await queue.get_job("nonexistent-job")

    assert job is None


@pytest.mark.asyncio
async def test_get_job_exists(queue, mock_redis):
    mock_redis.hgetall = AsyncMock(return_value={
        b"job_id": b"test-123",
        b"status": b"processing",
        b"progress": b"50",
        b"input_data": b'{"prompt": "test"}',
        b"parameters": b'{"seed": 42}'
    })

    job = await queue.get_job("test-123")

    assert job is not None
    assert job["job_id"] == "test-123"
    assert job["status"] == "processing"
    assert job["progress"] == 50
    assert job["input_data"] == {"prompt": "test"}


@pytest.mark.asyncio
async def test_update_job(queue, mock_redis):
    await queue.update_job("test-123", {"status": "completed", "progress": 100})

    mock_redis.hset.assert_called_once()
    call_kwargs = mock_redis.hset.call_args
    assert "job:test-123" in call_kwargs.args


@pytest.mark.asyncio
async def test_get_queue_size(queue, mock_redis):
    size = await queue.get_queue_size()

    assert size == 5
    mock_redis.llen.assert_called_once()


@pytest.mark.asyncio
async def test_get_pending_jobs(queue, mock_redis):
    jobs = await queue.get_pending_jobs(limit=10)

    assert len(jobs) == 2
    assert jobs[0] == "job-1"
    assert jobs[1] == "job-2"


@pytest.mark.asyncio
async def test_cancel_job_success(queue, mock_redis):
    mock_redis.hgetall = AsyncMock(return_value={
        b"job_id": b"test-123",
        b"status": b"queued"
    })

    result = await queue.cancel_job("test-123")

    assert result is True
    mock_redis.lrem.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_job_already_completed(queue, mock_redis):
    mock_redis.hgetall = AsyncMock(return_value={
        b"job_id": b"test-123",
        b"status": b"completed"
    })

    result = await queue.cancel_job("test-123")

    assert result is False
