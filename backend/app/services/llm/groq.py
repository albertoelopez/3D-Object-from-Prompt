import httpx
from typing import Optional, Tuple

from app.config import settings
from app.services.llm.base import BaseLLMProvider, ENHANCEMENT_SYSTEM_PROMPT


class GroqProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.default_model = settings.GROQ_DEFAULT_MODEL
        self.base_url = "https://api.groq.com/openai/v1"

    async def enhance_prompt(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> Tuple[str, str]:
        if not self.api_key:
            raise ValueError("Groq API key not configured")

        model = model or self.default_model

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": ENHANCEMENT_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Enhance this 3D object description: {prompt}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 256,
                    "top_p": 0.9
                }
            )
            response.raise_for_status()

            result = response.json()
            enhanced = result["choices"][0]["message"]["content"].strip()

            if not enhanced:
                enhanced = prompt

            return enhanced, model

    async def is_available(self) -> bool:
        return self.api_key is not None

    async def list_models(self) -> list:
        if not self.api_key:
            return []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            return []
