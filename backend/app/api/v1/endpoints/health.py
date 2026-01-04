from fastapi import APIRouter, Depends
from typing import Dict, Any
import httpx

from app.core.queue import JobQueue
from app.core.redis import get_redis
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


def get_queue() -> JobQueue:
    return JobQueue(get_redis())


async def check_redis_health() -> bool:
    try:
        redis = get_redis()
        await redis.ping()
        return True
    except Exception:
        return False


async def check_ollama_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            return response.status_code == 200
    except Exception:
        return False


async def check_groq_health() -> bool:
    return settings.GROQ_API_KEY is not None


@router.get("")
async def health_check(
    queue: JobQueue = Depends(get_queue)
) -> Dict[str, Any]:
    redis_healthy = await check_redis_health()
    ollama_healthy = await check_ollama_health()
    groq_available = await check_groq_health()

    queue_size = 0
    if redis_healthy:
        queue_size = await queue.get_queue_size()

    overall_status = "healthy" if redis_healthy else "degraded"

    return {
        "status": overall_status,
        "services": {
            "api": "healthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "ollama": "healthy" if ollama_healthy else "unavailable",
            "groq": "available" if groq_available else "not_configured"
        },
        "queue": {
            "pending": queue_size,
            "processing": 0,
            "workers_available": settings.WORKER_COUNT
        }
    }


@router.get("/ready")
async def readiness_check():
    redis_healthy = await check_redis_health()

    if not redis_healthy:
        return {"status": "not_ready", "reason": "Redis not available"}

    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    return {"status": "alive"}
