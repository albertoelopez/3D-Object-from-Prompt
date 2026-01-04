from abc import ABC, abstractmethod
from typing import Optional, Tuple


ENHANCEMENT_SYSTEM_PROMPT = """You are an expert 3D object description enhancer. Your task is to transform simple user prompts into detailed, precise descriptions optimized for 3D object generation.

For any input prompt, enhance it by adding:
1. Geometric details: precise shape characteristics, proportions, dimensions
2. Material properties: texture type, surface finish (glossy, matte, rough, smooth)
3. Material composition: specific materials (oak wood, brushed aluminum, ceramic, etc.)
4. Visual details: colors, patterns, decorative elements, design style
5. Physical properties: reflectivity, transparency, roughness values
6. Structural details: key components, assembly, parts relationship
7. Scale/size references: relative or absolute measurements
8. Artistic style: realism level, art movement, design era

Keep the enhanced prompt concise (2-4 sentences) but information-dense. Focus on details that help 3D generation models understand the object's structure, appearance, and materials.

Output ONLY the enhanced prompt, nothing else. Do not include any explanations or additional text."""


class BaseLLMProvider(ABC):
    @abstractmethod
    async def enhance_prompt(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> Tuple[str, str]:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass
