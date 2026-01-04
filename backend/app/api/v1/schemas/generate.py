from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class Resolution(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    GROQ = "groq"


class SamplerParams(BaseModel):
    steps: int = Field(default=12, ge=1, le=50)
    cfg_strength: float = Field(default=7.5, ge=0.0, le=20.0)


class TextTo3DRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    enhance_prompt: bool = Field(default=False)
    llm_provider: LLMProvider = Field(default=LLMProvider.OLLAMA)
    seed: Optional[int] = Field(default=None)
    resolution: Resolution = Field(default=Resolution.MEDIUM)
    sparse_structure_sampler_params: Optional[SamplerParams] = None
    slat_sampler_params: Optional[SamplerParams] = None


class ImageTo3DRequest(BaseModel):
    enhance_prompt: bool = Field(default=False)
    llm_provider: LLMProvider = Field(default=LLMProvider.OLLAMA)
    seed: Optional[int] = Field(default=None)
    resolution: Resolution = Field(default=Resolution.MEDIUM)
    sparse_structure_sampler_params: Optional[SamplerParams] = None
    slat_sampler_params: Optional[SamplerParams] = None


class GenerationResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    estimated_time: int
    websocket_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "queued",
                "created_at": "2026-01-03T12:00:00Z",
                "estimated_time": 120,
                "websocket_url": "ws://localhost:8000/ws/jobs/550e8400-e29b-41d4-a716-446655440000"
            }
        }
