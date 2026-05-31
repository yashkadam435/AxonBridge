"""
Speech-to-Text Engine (Whisper Stub)
"""

from pydantic import BaseModel
from typing import List, Optional

class WordToken(BaseModel):
    word: str
    start: float
    end: float
    confidence: float
    is_medical_term: bool = False

class TranscriptionSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    words: List[WordToken]
    language: str
    confidence: float

class TranscriptionResult(BaseModel):
    text: str
    segments: List[TranscriptionSegment]
    detected_language: str
    language_confidence: float
    duration_seconds: float
    code_switched_languages: List[str]
    medical_terms_found: List[str]
    confidence_score: float

class WhisperEngine:
    """
    Self-hosted OpenAI Whisper large-v3 for speech-to-text.
    """
    
    def __init__(self):
        self.model_loaded = False
        # self.model = faster_whisper.WhisperModel("large-v3")
        
    async def transcribe(self, audio_bytes: bytes, language: str = None) -> TranscriptionResult:
        # Stubbed inference
        return TranscriptionResult(
            text="Patient presents with acute chest pain.",
            segments=[
                TranscriptionSegment(
                    id=1, start=0.0, end=2.0, text="Patient presents with acute chest pain.",
                    words=[], language="en", confidence=0.99
                )
            ],
            detected_language="en",
            language_confidence=0.99,
            duration_seconds=2.0,
            code_switched_languages=[],
            medical_terms_found=["acute chest pain"],
            confidence_score=0.98
        )
