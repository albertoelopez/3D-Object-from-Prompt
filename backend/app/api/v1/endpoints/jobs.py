from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.api.v1.schemas import JobResponse, JobListResponse, JobStatus, JobResult, JobError
from app.core.queue import JobQueue
from app.core.redis import get_redis
from app.core.storage import storage_service
from app.config import settings

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_queue() -> JobQueue:
    return JobQueue(get_redis())


def format_job_response(job: dict) -> JobResponse:
    result = None
    if job.get("result"):
        result = JobResult(
            glb_url=job["result"].get("glb_url"),
            ply_url=job["result"].get("ply_url"),
            preview_url=job["result"].get("preview_url"),
            file_sizes=job["result"].get("file_sizes")
        )

    error = None
    if job.get("error"):
        error = JobError(
            code=job["error"].get("code", "UNKNOWN"),
            message=job["error"].get("message", "Unknown error"),
            recoverable=job["error"].get("recoverable", False)
        )

    input_data = None
    if job.get("input_data"):
        input_data = {
            "type": job["input_data"].get("type"),
            "prompt": job["input_data"].get("prompt"),
            "enhanced_prompt": job["input_data"].get("enhanced_prompt"),
            "image_filename": job["input_data"].get("image_filename"),
            "parameters": job.get("parameters", {})
        }

    return JobResponse(
        job_id=job["job_id"],
        status=JobStatus(job["status"]),
        progress=job.get("progress", 0),
        stage=job.get("stage"),
        stage_progress=job.get("stage_progress", 0),
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        input=input_data,
        result=result,
        error=error
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return format_job_response(job)


@router.delete("/{job_id}")
async def cancel_job(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    cancelled = await queue.cancel_job(job_id)
    if not cancelled:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in status: {job['status']}"
        )

    return {"job_id": job_id, "status": "cancelled", "message": "Job cancelled successfully"}


@router.get("", response_model=JobListResponse)
async def list_jobs(
    limit: int = 10,
    queue: JobQueue = Depends(get_queue)
):
    pending_job_ids = await queue.get_pending_jobs(limit=limit)
    jobs = []

    for job_id in pending_job_ids:
        job = await queue.get_job(job_id)
        if job:
            jobs.append(format_job_response(job))

    queue_size = await queue.get_queue_size()

    return JobListResponse(
        jobs=jobs,
        total=len(jobs),
        queue_size=queue_size
    )
