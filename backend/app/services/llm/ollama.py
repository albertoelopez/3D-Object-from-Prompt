import httpx
from typing import Optional, Tuple

from app.config import settings
from app.services.llm.base import BaseLLMProvider, ENHANCEMENT_SYSTEM_PROMPT


class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_DEFAULT_MODEL

    async def enhance_prompt(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> Tuple[str, str]:
        model = model or self.default_model

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": f"{ENHANCEMENT_SYSTEM_PROMPT}\n\nOriginal prompt: {prompt}\n\nEnhanced prompt:",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 256
                    }
                }
            )
            response.raise_for_status()

            result = response.json()
            enhanced = result.get("response", prompt).strip()

            if not enhanced:
                enhanced = prompt

            return enhanced, model

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []
