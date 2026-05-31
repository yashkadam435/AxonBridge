import asyncio
import json
import time
import os
from groq import AsyncGroq
from app.models.schemas import BotRequest, BotResponse
from app.axonmd.bot_definitions import BOT_DEFINITIONS

class AxonMDBotClient:
    """
    Integrates AxonMD specialty bots as tool-calling endpoints.
    Uses Groq LLM under the hood to simulate the reasoning of different specialties.
    """
    
    def __init__(self):
        # We will use the async Groq client
        self.groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", "your_groq_api_key_here"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    async def invoke_bot(self, specialty: str, clinical_context: dict, timeout: int = 15) -> BotResponse:
        start_time = time.time()
        
        # Verify specialty
        if specialty not in BOT_DEFINITIONS:
            # Fallback
            specialty = "general_medicine"
            
        system_prompt = f"""You are the AxonMD {specialty.replace('_', ' ').title()} Bot.
        Your task is to analyze the following clinical context and provide a JSON response.
        Focus your analysis strictly from the perspective of {specialty.replace('_', ' ').title()}.
        
        Provide the response in the following strict JSON format:
        {{
            "differentials": [{{ "diagnosis": "...", "probability": "High/Medium/Low", "reasoning": "..." }}],
            "investigations": ["...", "..."],
            "treatment_recommendations": ["...", "..."],
            "red_flags": ["...", "..."],
            "confidence": 0.85
        }}
        
        Respond ONLY with valid JSON.
        """
        
        user_prompt = f"Clinical Context: {json.dumps(clinical_context, default=str)}"
        
        try:
            # Enforce timeout using asyncio.wait_for
            response = await asyncio.wait_for(
                self.groq_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                ),
                timeout=timeout
            )
            
            content = json.loads(response.choices[0].message.content)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return BotResponse(
                specialty=specialty,
                bot_version="1.0.0",
                response_type="comprehensive",
                content=content,
                confidence=content.get("confidence", 0.7),
                citations=[f"AxonMD {specialty.title()} reasoning engine"],
                requires_immediate_attention=len(content.get("red_flags", [])) > 0,
                processing_time_ms=processing_time,
                cached=False
            )
        except asyncio.TimeoutError:
            print(f"[{specialty} bot] Request timed out after {timeout} seconds.")
            return await self.invoke_with_fallback("general_medicine", clinical_context)
        except Exception as e:
            print(f"[{specialty} bot] Error: {str(e)}")
            return BotResponse(
                specialty=specialty,
                bot_version="1.0.0",
                response_type="error",
                content={"error": str(e)},
                confidence=0.0,
                requires_immediate_attention=False,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

    async def route_by_context(self, symptoms: list, department: str = None, diagnosis: str = None) -> str:
        """Simple rule-based router based on triggers."""
        # Convert symptoms to a single string for easy searching
        symptoms_str = " ".join(symptoms).lower()
        
        # Check emergency priority first
        for word in ["cardiac arrest", "stroke", "trauma", "unconscious", "gsw", "severe bleeding"]:
            if word in symptoms_str:
                return "emergency_medicine"
                
        # Check specific triggers
        best_match = "general_medicine"
        max_matches = 0
        
        for spec, details in BOT_DEFINITIONS.items():
            triggers = details.get("triggers", [])
            matches = sum(1 for t in triggers if t.lower() in symptoms_str or t.lower() == (department or "").lower())
            if matches > max_matches:
                max_matches = matches
                best_match = spec
                
        return best_match

    async def invoke_with_fallback(self, primary: str, context: dict) -> BotResponse:
        """Invoke primary, fallback to general_medicine if failed."""
        return await self.invoke_bot("general_medicine", context)

    async def batch_invoke(self, requests: list[BotRequest]) -> list[BotResponse]:
        """Invoke multiple bots in parallel."""
        tasks = []
        for req in requests:
            # Combine context
            ctx = {
                "patient_context": req.patient_context,
                "symptoms": req.symptoms,
                "vitals": req.vital_signs,
                "medications": req.current_medications
            }
            tasks.append(self.invoke_bot(req.specialty, ctx))
            
        return await asyncio.gather(*tasks)
