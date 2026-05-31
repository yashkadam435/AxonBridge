"""
DOM Analyzer
"""

from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from playwright.async_api import Page, ElementHandle

class DOMElement(BaseModel):
    id: Optional[str]
    tag: str
    type: Optional[str]
    name: Optional[str]
    class_list: List[str]
    text_content: Optional[str]
    aria_label: Optional[str]
    placeholder: Optional[str]
    value: Optional[str]
    selector: str
    selector_priority: int
    bounding_box: Dict[str, float]
    is_visible: bool
    is_interactive: bool
    is_enabled: bool

class DOMSnapshot(BaseModel):
    url: str
    title: str
    viewport: Dict[str, int]
    elements: List[DOMElement]
    dynamic_regions: List[str]

class DOMAnalyzer:
    async def analyze_page(self, page: Page) -> DOMSnapshot:
        """Analyze the DOM structure of a web page to identify interactive elements."""
        
        # We inject a JavaScript function to analyze the DOM locally
        script = """
        () => {
            const isInteractive = (el) => {
                const tag = el.tagName.toLowerCase();
                if (['a', 'button', 'input', 'select', 'textarea'].includes(tag)) return true;
                if (el.hasAttribute('onclick') || el.hasAttribute('tabindex')) return true;
                if (el.getAttribute('role') === 'button') return true;
                return false;
            };

            const getUniqueSelector = (el) => {
                if (el.id) return `#${el.id}`;
                if (el.getAttribute('data-testid')) return `[data-testid="${el.getAttribute('data-testid')}"]`;
                
                let path = [];
                let current = el;
                while (current && current.nodeType === Node.ELEMENT_NODE) {
                    let selector = current.nodeName.toLowerCase();
                    if (current.id) {
                        selector += `#${current.id}`;
                        path.unshift(selector);
                        break;
                    } else {
                        let sib = current, nth = 1;
                        while (sib = sib.previousElementSibling) {
                            if (sib.nodeName.toLowerCase() == selector) nth++;
                        }
                        if (nth != 1) selector += `:nth-of-type(${nth})`;
                    }
                    path.unshift(selector);
                    current = current.parentNode;
                }
                return path.join(' > ');
            };

            const elements = [];
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT, null, false);
            
            let node;
            while (node = walker.nextNode()) {
                if (!isInteractive(node)) continue;
                
                const rect = node.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) continue;
                
                elements.push({
                    id: node.id || null,
                    tag: node.tagName.toLowerCase(),
                    type: node.type || null,
                    name: node.name || null,
                    class_list: Array.from(node.classList),
                    text_content: node.innerText || null,
                    aria_label: node.getAttribute('aria-label') || null,
                    placeholder: node.getAttribute('placeholder') || null,
                    value: node.value || null,
                    selector: getUniqueSelector(node),
                    selector_priority: node.id ? 1 : (node.getAttribute('data-testid') ? 2 : 5),
                    bounding_box: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                    is_visible: true, // simplified
                    is_interactive: true,
                    is_enabled: !node.disabled
                });
            }
            
            return {
                url: window.location.href,
                title: document.title,
                viewport: {width: window.innerWidth, height: window.innerHeight},
                elements: elements,
                dynamic_regions: []
            };
        }
        """
        
        result = await page.evaluate(script)
        
        return DOMSnapshot(
            url=result["url"],
            title=result["title"],
            viewport=result["viewport"],
            elements=[DOMElement(**el) for el in result["elements"]],
            dynamic_regions=result["dynamic_regions"]
        )

    async def find_element(self, page: Page, selector: str, timeout: int = 5000) -> ElementHandle:
        return await page.wait_for_selector(selector, timeout=timeout)
