from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from datetime import datetime
import json

from app.api.v1.schemas import (
    TextTo3DRequest,
    GenerationResponse,
    Resolution,
    LLMProvider
)
from app.core.queue import JobQueue
from app.core.redis import get_redis
from app.core.storage import storage_service
from app.core.exceptions import InvalidFileTypeException, FileTooLargeException
from app.config import settings

router = APIRouter(prefix="/generate", tags=["generation"])


def get_queue() -> JobQueue:
    return JobQueue(get_redis())


def get_estimated_time(resolution: Resolution) -> int:
    estimates = {
        Resolution.LOW: 60,
        Resolution.MEDIUM: 120,
        Resolution.HIGH: 180
    }
    return estimates.get(resolution, 120)


@router.post("/text-to-3d", response_model=GenerationResponse)
async def generate_text_to_3d(
    request: TextTo3DRequest,
    queue: JobQueue = Depends(get_queue)
):
    input_data = {
        "type": "text",
        "prompt": request.prompt,
        "enhance_prompt": request.enhance_prompt,
        "llm_provider": request.llm_provider.value
    }

    parameters = {
        "seed": request.seed,
        "resolution": request.resolution.value,
        "sparse_structure_sampler_params": request.sparse_structure_sampler_params.model_dump() if request.sparse_structure_sampler_params else None,
        "slat_sampler_params": request.slat_sampler_params.model_dump() if request.slat_sampler_params else None
    }

    job_id = await queue.enqueue(
        job_type="text_to_3d",
        input_data=input_data,
        parameters=parameters
    )

    job = await queue.get_job(job_id)

    return GenerationResponse(
        job_id=job_id,
        status=job["status"],
        created_at=job["created_at"],
        estimated_time=get_estimated_time(request.resolution),
        websocket_url=f"ws://localhost:{settings.API_PORT}/ws/jobs/{job_id}"
    )


@router.post("/image-to-3d", response_model=GenerationResponse)
async def generate_image_to_3d(
    file: UploadFile = File(...),
    enhance_prompt: bool = Form(default=False),
    llm_provider: str = Form(default="ollama"),
    seed: Optional[int] = Form(default=None),
    resolution: str = Form(default="medium"),
    sparse_structure_sampler_params: Optional[str] = Form(default=None),
    slat_sampler_params: Optional[str] = Form(default=None),
    queue: JobQueue = Depends(get_queue)
):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes"
        )

    filename = await storage_service.save_upload(content, file.filename)

    input_data = {
        "type": "image",
        "image_filename": filename,
        "enhance_prompt": enhance_prompt,
        "llm_provider": llm_provider
    }

    ss_params = None
    if sparse_structure_sampler_params:
        try:
            ss_params = json.loads(sparse_structure_sampler_params)
        except json.JSONDecodeError:
            pass

    slat_params = None
    if slat_sampler_params:
        try:
            slat_params = json.loads(slat_sampler_params)
        except json.JSONDecodeError:
            pass

    parameters = {
        "seed": seed,
        "resolution": resolution,
        "sparse_structure_sampler_params": ss_params,
        "slat_sampler_params": slat_params
    }

    job_id = await queue.enqueue(
        job_type="image_to_3d",
        input_data=input_data,
        parameters=parameters
    )

    job = await queue.get_job(job_id)
    res = Resolution(resolution)

    return GenerationResponse(
        job_id=job_id,
        status=job["status"],
        created_at=job["created_at"],
        estimated_time=get_estimated_time(res),
        websocket_url=f"ws://localhost:{settings.API_PORT}/ws/jobs/{job_id}"
    )
