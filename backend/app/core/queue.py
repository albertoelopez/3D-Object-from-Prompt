import json
from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime
import redis.asyncio as redis

from app.config import settings


class JobQueue:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.queue_name = settings.WORKER_QUEUE_NAME

    async def enqueue(
        self,
        job_type: str,
        input_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> str:
        job_id = str(uuid4())

        job_data = {
            "job_id": job_id,
            "job_type": job_type,
            "status": "queued",
            "input_data": input_data,
            "parameters": parameters,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "progress": 0,
            "stage": "queued",
            "stage_progress": 0
        }

        await self.redis.hset(
            f"job:{job_id}",
            mapping={
                k: json.dumps(v) if isinstance(v, (dict, list)) else (str(v) if v is not None else "")
                for k, v in job_data.items()
            }
        )

        await self.redis.rpush(self.queue_name, job_id)
        await self.redis.expire(f"job:{job_id}", settings.JOB_RETENTION_HOURS * 3600)

        return job_id

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        job_data = await self.redis.hgetall(f"job:{job_id}")
        if not job_data:
            return None

        result = {}
        for k, v in job_data.items():
            key = k.decode() if isinstance(k, bytes) else k
            value = v.decode() if isinstance(v, bytes) else v

            if key in ["input_data", "parameters", "result", "error"]:
                try:
                    result[key] = json.loads(value) if value else None
                except json.JSONDecodeError:
                    result[key] = value
            elif key in ["progress", "stage_progress"]:
                try:
                    result[key] = int(value) if value else 0
                except ValueError:
                    result[key] = 0
            else:
                result[key] = value

        return result

    async def update_job(self, job_id: str, updates: Dict[str, Any]):
        mapping = {}
        for k, v in updates.items():
            if isinstance(v, (dict, list)):
                mapping[k] = json.dumps(v)
            elif v is None:
                mapping[k] = ""
            else:
                mapping[k] = str(v)

        await self.redis.hset(f"job:{job_id}", mapping=mapping)

    async def get_queue_size(self) -> int:
        return await self.redis.llen(self.queue_name)

    async def get_pending_jobs(self, limit: int = 10) -> List[str]:
        jobs = await self.redis.lrange(self.queue_name, 0, limit - 1)
        return [j.decode() if isinstance(j, bytes) else j for j in jobs]

    async def cancel_job(self, job_id: str) -> bool:
        job = await self.get_job(job_id)
        if not job:
            return False

        if job["status"] in ["completed", "failed", "cancelled"]:
            return False

        await self.update_job(job_id, {
            "status": "cancelled",
            "completed_at": datetime.utcnow().isoformat()
        })

        await self.redis.lrem(self.queue_name, 0, job_id)
        return True
