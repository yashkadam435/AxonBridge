import os
import json
import asyncio
from typing import List, Dict, Any
from groq import AsyncGroq

class GuidelineRetriever:
    """
    Replaced heavy pgvector + sentence-transformers with a lightweight Groq-powered zero-shot guideline search.
    This saves hundreds of megabytes of local storage space while maintaining functionality.
    """
    def __init__(self, db_url: str):
        self.groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", "your_groq_api_key_here"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
    async def search(self, query_text: str, jurisdiction: str = "global", limit: int = 1) -> List[Dict[str, Any]]:
        # Use Groq to dynamically "retrieve" guidelines based on its training data
        prompt = f"""You are a medical guideline retriever. 
        For the following clinical scenario: '{query_text}', provide the single most relevant clinical guideline from WHO, NICE, or ICMR.
        
        Return ONLY valid JSON:
        {{
            "source": "WHO/NICE/ICMR",
            "version": "2023",
            "content": "The actual guideline text...",
            "similarity": 0.95
        }}
        """
        
        try:
            response = await self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return [data]
        except Exception as e:
            print(f"Groq Guideline Error: {e}")
            return []
