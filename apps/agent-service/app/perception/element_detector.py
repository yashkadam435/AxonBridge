"""
Element Detector (Hybrid DOM + CV)
"""

from typing import Dict, Any, Optional
from playwright.async_api import Page
from pydantic import BaseModel

from .dom_analyzer import DOMAnalyzer, DOMSnapshot
from .vision_pipeline import VisionPipeline

class LocatedElement(BaseModel):
    found_via: str  # "dom" or "cv"
    selector: Optional[str]
    bbox: Dict[str, float]
    confidence: float

class ElementDetector:
    """
    Hybrid detection system combining DOM analysis and Computer Vision.
    Uses DOM as primary, CV as fallback for obfuscated or canvas-rendered UIs.
    """
    
    def __init__(self, dom_analyzer: DOMAnalyzer, vision_pipeline: VisionPipeline):
        self.dom = dom_analyzer
        self.cv = vision_pipeline

    async def find_element(self, page: Page, description: str, selector_hint: str = None, use_cv_fallback: bool = True) -> LocatedElement:
        # 1. Try DOM based detection first
        dom_snapshot = await self.dom.analyze_page(page)
        
        # Simple heuristic: Check if selector_hint matches anything
        if selector_hint:
            for el in dom_snapshot.elements:
                if el.selector == selector_hint or selector_hint in el.class_list or el.id == selector_hint:
                    return LocatedElement(
                        found_via="dom",
                        selector=el.selector,
                        bbox=el.bounding_box,
                        confidence=1.0
                    )
        
        # Try semantic matching by text or name
        for el in dom_snapshot.elements:
            if description.lower() in (el.text_content or "").lower() or \
               description.lower() in (el.aria_label or "").lower() or \
               description.lower() in (el.name or "").lower():
                return LocatedElement(
                    found_via="dom",
                    selector=el.selector,
                    bbox=el.bounding_box,
                    confidence=0.85
                )
                
        # 2. Fallback to CV if enabled and DOM fails
        if use_cv_fallback:
            screenshot = await page.screenshot()
            
            # Use LLM to find the element based on description
            # In a real impl, we'd pass the screenshot to analyze_screenshot_llm
            # and ask it for the bounding box of `description`.
            analysis = await self.cv.analyze_screenshot_llm(screenshot, f"Find the bounding box for the UI element: {description}")
            
            # Mock CV result for the sake of architecture
            return LocatedElement(
                found_via="cv",
                selector=None,
                bbox={"x": 100, "y": 200, "width": 50, "height": 30},
                confidence=0.75
            )
            
        raise ValueError(f"Could not locate element matching: {description}")
