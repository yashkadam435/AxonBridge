"""
Vision Pipeline (Stubbed for Lightweight Demo)
"""

import io
import base64
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DetectedElement(BaseModel):
    class_name: str
    confidence: float
    bbox: Dict[str, int] # x, y, width, height

class UIChange(BaseModel):
    change_type: str
    severity: float
    bbox: Dict[str, int]

class VisionPipeline:
    def __init__(self):
        self.model = None

    async def detect_elements_cv(self, screenshot: bytes, confidence_threshold: float = 0.65) -> List[DetectedElement]:
        """Stubbed: Fallback to DOM instead of CV for lightweight demo."""
        return []

    async def analyze_screenshot_llm(self, screenshot: bytes, prompt: str, his_context: Dict = None) -> Dict[str, Any]:
        """Analyze UI state using multimodal LLM via API"""
        return {"status": "mock_llm_response", "analysis": "Mock analysis of screenshot"}

    async def extract_text_ocr(self, screenshot: bytes, region: Dict = None) -> List[Dict[str, str]]:
        """Stubbed: Fallback to DOM text content for lightweight demo."""
        return [{"text": "Extracted text via DOM fallback"}]

    async def detect_ui_changes(self, baseline_screenshot: bytes, current_screenshot: bytes) -> List[UIChange]:
        """Stubbed: Fallback to DOM diffing for lightweight demo."""
        return []
