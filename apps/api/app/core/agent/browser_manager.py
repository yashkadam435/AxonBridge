"""
AxonBridge — Playwright Browser Manager
"""

import uuid
from typing import Optional, AsyncGenerator

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def start(self) -> None:
        """Initialize Playwright and launch the browser."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-dev-shm-usage", "--no-sandbox"]
        )

    async def stop(self) -> None:
        """Close the browser and stop Playwright."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def create_isolated_context(self) -> BrowserContext:
        """Create a new isolated incognito browser context."""
        if not self._browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="AxonBridge/1.0 (Clinical Automation Agent)",
            record_video_dir="/tmp/playwright_videos"  # Save videos to tmp
        )
        return context

    async def take_screenshot(self, page: Page, path: str) -> None:
        """Take a full page screenshot."""
        await page.screenshot(path=path, full_page=True)


# Dependency provider
_browser_manager: Optional[BrowserManager] = None

async def init_browser() -> None:
    global _browser_manager
    _browser_manager = BrowserManager(headless=True)
    await _browser_manager.start()

async def get_browser() -> BrowserManager:
    if not _browser_manager:
        raise RuntimeError("BrowserManager not initialized")
    return _browser_manager

async def stop_browser() -> None:
    global _browser_manager
    if _browser_manager:
        await _browser_manager.stop()
        _browser_manager = None
