"""
AxonBridge — Agent Orchestrator

Handles the execution logic for clinical workflows using Playwright.
"""

import asyncio
from typing import Any, Dict
from datetime import datetime, UTC

from playwright.async_api import Page
from .browser_manager import get_browser

class WorkflowAgent:
    def __init__(self, execution_id: str, target_url: str):
        self.execution_id = execution_id
        self.target_url = target_url
        self.status = "pending"
        self._context = None
        self._page = None

    async def initialize(self) -> None:
        """Initialize the browser session for this agent."""
        browser_manager = await get_browser()
        self._context = await browser_manager.create_isolated_context()
        self._page = await self._context.new_page()
        self.status = "initializing"

    async def execute_step(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        action = step_config.get("action")
        selector = step_config.get("selector")
        value = step_config.get("value")

        result = {
            "status": "success",
            "action": action,
            "timestamp": datetime.now(UTC).isoformat()
        }

        try:
            if action == "navigate":
                await self._page.goto(self.target_url)
            
            elif action == "click":
                await self._page.click(selector, timeout=5000)
            
            elif action == "type":
                await self._page.fill(selector, value, timeout=5000)
            
            elif action == "extract":
                element = await self._page.wait_for_selector(selector, timeout=5000)
                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                if tag_name in ["input", "textarea"]:
                    extracted_text = await element.input_value()
                else:
                    extracted_text = await element.inner_text()
                result["extracted_value"] = extracted_text
            
            else:
                result["status"] = "failed"
                result["error"] = f"Unknown action: {action}"
                
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def close(self) -> None:
        """Close the agent session."""
        if self._context:
            await self._context.close()
        self.status = "terminated"
