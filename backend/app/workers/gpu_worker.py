import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
import redis

from app.config import settings
from app.core.queue import JobQueue
from app.core.storage import storage_service
from app.services.trellis.pipeline import trellis_pipeline
from app.services.llm.ollama import OllamaProvider
from app.services.llm.groq import GroqProvider


class GPUWorker:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.sync_redis: Optional[redis.Redis] = None
        self.queue: Optional[JobQueue] = None
        self.ollama_provider = OllamaProvider()
        self.groq_provider = GroqProvider()
        self.running = False

    async def initialize(self):
        self.redis = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=False
        )

        self.sync_redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=False
        )

        self.queue = JobQueue(self.redis)

        print("Initializing TRELLIS pipeline...")
        trellis_pipeline.initialize()
        print("Worker initialized successfully")

    async def broadcast_progress(self, job_id: str, message: Dict[str, Any]):
        message["timestamp"] = datetime.utcnow().isoformat()
        await self.redis.publish(f"job:{job_id}:progress", json.dumps(message))

    def create_progress_callback(self, job_id: str):
        def callback(progress: int, stage: str, stage_progress: int):
            self.sync_redis.hset(
                f"job:{job_id}",
                mapping={
                    "progress": str(progress),
                    "stage": stage,
                    "stage_progress": str(stage_progress)
                }
            )

            self.sync_redis.publish(
                f"job:{job_id}:progress",
                json.dumps({
                    "type": "progress_update",
                    "job_id": job_id,
                    "progress": progress,
                    "stage": stage,
                    "stage_progress": stage_progress,
                    "message": f"Stage: {stage} ({stage_progress}%)",
                    "timestamp": datetime.utcnow().isoformat()
                })
            )

        return callback

    async def enhance_prompt(self, prompt: str, provider: str) -> str:
        try:
            if provider == "ollama":
                enhanced, _ = await self.ollama_provider.enhance_prompt(prompt)
            else:
                enhanced, _ = await self.groq_provider.enhance_prompt(prompt)
            return enhanced
        except Exception as e:
            print(f"Prompt enhancement failed: {e}")
            return prompt

    async def process_job(self, job_id: str):
        job_data = await self.queue.get_job(job_id)
        if not job_data:
            print(f"Job {job_id} not found")
            return

        print(f"Processing job {job_id}...")

        await self.queue.update_job(job_id, {
            "status": "processing",
            "started_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "stage": "initializing"
        })

        await self.broadcast_progress(job_id, {
            "type": "status_update",
            "job_id": job_id,
            "status": "processing"
        })

        try:
            job_type = job_data["job_type"]
            input_data = job_data["input_data"]
            parameters = job_data["parameters"]

            enhanced_prompt = None
            if input_data.get("enhance_prompt"):
                await self.queue.update_job(job_id, {
                    "stage": "enhancing_prompt",
                    "progress": 5
                })

                prompt = input_data.get("prompt", "")
                if prompt:
                    enhanced_prompt = await self.enhance_prompt(
                        prompt,
                        input_data.get("llm_provider", "ollama")
                    )
                    input_data["enhanced_prompt"] = enhanced_prompt
                    await self.queue.update_job(job_id, {"input_data": input_data})

            progress_callback = self.create_progress_callback(job_id)

            if job_type == "text_to_3d":
                prompt_to_use = enhanced_prompt or input_data.get("prompt", "")
                result = trellis_pipeline.generate_from_text(
                    prompt=prompt_to_use,
                    job_id=job_id,
                    seed=parameters.get("seed"),
                    resolution=parameters.get("resolution", "medium"),
                    sparse_structure_sampler_params=parameters.get("sparse_structure_sampler_params"),
                    slat_sampler_params=parameters.get("slat_sampler_params"),
                    progress_callback=progress_callback
                )
            elif job_type == "image_to_3d":
                image_path = storage_service.get_upload_path(input_data["image_filename"])
                if not image_path:
                    raise FileNotFoundError(f"Image not found: {input_data['image_filename']}")

                result = trellis_pipeline.generate_from_image(
                    image_path=str(image_path),
                    job_id=job_id,
                    seed=parameters.get("seed"),
                    resolution=parameters.get("resolution", "medium"),
                    sparse_structure_sampler_params=parameters.get("sparse_structure_sampler_params"),
                    slat_sampler_params=parameters.get("slat_sampler_params"),
                    progress_callback=progress_callback
                )
            else:
                raise ValueError(f"Unknown job type: {job_type}")

            job_result = {
                "glb_url": f"/api/v1/download/{job_id}.glb" if result.get("glb_path") else None,
                "ply_url": f"/api/v1/download/{job_id}.ply" if result.get("ply_path") else None,
                "preview_url": f"/api/v1/download/preview/{job_id}.png" if result.get("preview_path") else None,
                "file_sizes": result.get("file_sizes", {})
            }

            await self.queue.update_job(job_id, {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "result": job_result,
                "progress": 100,
                "stage": "completed"
            })

            await self.broadcast_progress(job_id, {
                "type": "completion",
                "job_id": job_id,
                "status": "completed",
                "result": job_result
            })

            print(f"Job {job_id} completed successfully")

        except Exception as e:
            print(f"Job {job_id} failed: {e}")

            await self.queue.update_job(job_id, {
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "error": {
                    "code": "PROCESSING_ERROR",
                    "message": str(e),
                    "recoverable": False
                }
            })

            await self.broadcast_progress(job_id, {
                "type": "error",
                "job_id": job_id,
                "error": {
                    "code": "PROCESSING_ERROR",
                    "message": str(e)
                }
            })

    async def run(self):
        await self.initialize()
        self.running = True

        print(f"Worker started, listening on queue: {settings.WORKER_QUEUE_NAME}")

        while self.running:
            try:
                result = await self.redis.blpop(
                    settings.WORKER_QUEUE_NAME,
                    timeout=5
                )

                if result:
                    _, job_id = result
                    job_id = job_id.decode() if isinstance(job_id, bytes) else job_id
                    await self.process_job(job_id)

            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(1)

    async def stop(self):
        self.running = False
        if self.redis:
            await self.redis.close()
        if self.sync_redis:
            self.sync_redis.close()


async def main():
    worker = GPUWorker()
    try:
        await worker.run()
    except KeyboardInterrupt:
        print("Shutting down worker...")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
