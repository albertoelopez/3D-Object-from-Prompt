from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.queue import JobQueue
from app.core.redis import get_redis
from app.core.storage import storage_service

router = APIRouter(prefix="/download", tags=["download"])


def get_queue() -> JobQueue:
    return JobQueue(get_redis())


@router.get("/{job_id}.glb")
async def download_glb(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job not completed (status: {job['status']})")

    file_path = storage_service.get_output_path(job_id, "glb")
    if not file_path:
        raise HTTPException(status_code=404, detail="GLB file not found")

    return FileResponse(
        path=file_path,
        filename=f"{job_id}.glb",
        media_type="model/gltf-binary"
    )


@router.get("/{job_id}.ply")
async def download_ply(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job not completed (status: {job['status']})")

    file_path = storage_service.get_output_path(job_id, "ply")
    if not file_path:
        raise HTTPException(status_code=404, detail="PLY file not found")

    return FileResponse(
        path=file_path,
        filename=f"{job_id}.ply",
        media_type="application/x-ply"
    )


@router.get("/preview/{job_id}.png")
async def download_preview(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job not completed (status: {job['status']})")

    file_path = storage_service.get_preview_path(job_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Preview not found")

    return FileResponse(
        path=file_path,
        filename=f"{job_id}_preview.png",
        media_type="image/png"
    )
