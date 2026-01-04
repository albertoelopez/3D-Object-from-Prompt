from fastapi import APIRouter, HTTPException

from app.api.v1.schemas import PromptEnhanceRequest, PromptEnhanceResponse, LLMProvider
from app.services.llm.ollama import OllamaProvider
from app.services.llm.groq import GroqProvider

router = APIRouter(prefix="/prompts", tags=["prompts"])

ollama_provider = OllamaProvider()
groq_provider = GroqProvider()


@router.post("/enhance", response_model=PromptEnhanceResponse)
async def enhance_prompt(request: PromptEnhanceRequest):
    try:
        if request.provider == LLMProvider.OLLAMA:
            enhanced, model_used = await ollama_provider.enhance_prompt(
                request.prompt,
                model=request.model
            )
        else:
            enhanced, model_used = await groq_provider.enhance_prompt(
                request.prompt,
                model=request.model
            )

        return PromptEnhanceResponse(
            original_prompt=request.prompt,
            enhanced_prompt=enhanced,
            provider=request.provider.value,
            model_used=model_used
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance prompt: {str(e)}"
        )
