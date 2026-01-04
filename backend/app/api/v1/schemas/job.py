from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobResult(BaseModel):
    glb_url: Optional[str] = None
    ply_url: Optional[str] = None
    preview_url: Optional[str] = None
    file_sizes: Optional[Dict[str, int]] = None


class JobError(BaseModel):
    code: str
    message: str
    recoverable: bool = False


class JobInput(BaseModel):
    type: str
    prompt: Optional[str] = None
    enhanced_prompt: Optional[str] = None
    image_filename: Optional[str] = None
    parameters: Dict[str, Any] = {}


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = 0
    stage: Optional[str] = None
    stage_progress: int = 0
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    input: Optional[JobInput] = None
    result: Optional[JobResult] = None
    error: Optional[JobError] = None


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    queue_size: int
