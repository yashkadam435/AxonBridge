"""
LLM Client Wrapper (Groq)
"""
import os
import json
from typing import Dict, Any, Type
from pydantic import BaseModel
from groq import AsyncGroq
import structlog

logger = structlog.get_logger()

class LLMClient:
    """Wrapper around Groq APIs for structured outputs."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not api_key:
            logger.warning("GROQ_API_KEY is missing. LLM capabilities will fail or use mock data.")
            
        self.client = AsyncGroq(api_key=api_key)

    async def generate_structured(self, prompt: str, schema: Type[BaseModel], system_prompt: str = "You are a helpful AI assistant.") -> BaseModel:
        """Generates a structured Pydantic response from the LLM."""
        if not self.client.api_key or self.client.api_key == "":
            logger.warning("Mocking LLM response due to missing API key")
            return schema.model_construct()

        try:
            # We use JSON mode or standard function calling
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + f"\nOutput MUST be valid JSON adhering to this schema: {schema.model_json_schema()}"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return schema.model_validate_json(content)
            
        except Exception as e:
            logger.error("LLM Generation failed", error=str(e))
            raise e

llm_client = LLMClient()
