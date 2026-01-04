from pydantic import BaseModel, Field
from typing import Optional
from app.api.v1.schemas.generate import LLMProvider


class PromptEnhanceRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    provider: LLMProvider = Field(default=LLMProvider.OLLAMA)
    model: Optional[str] = None


class PromptEnhanceResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    provider: str
    model_used: str

    class Config:
        json_schema_extra = {
            "example": {
                "original_prompt": "a robot",
                "enhanced_prompt": "A futuristic humanoid robot with sleek metallic surfaces, glowing blue LED eyes, articulated joints, standing in a neutral pose with detailed mechanical components visible",
                "provider": "ollama",
                "model_used": "llama3.2"
            }
        }
