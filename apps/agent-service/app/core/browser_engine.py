"""
Browser Engine (Playwright Manager)
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class BrowserEngine:
    def __init__(self):
        self._playwright = None
        self._browser = None

    async def launch_browser(self, browser_type: str = "chromium", headless: bool = True) -> Browser:
        if not self._playwright:
            self._playwright = await async_playwright().start()
            
        if browser_type == "chromium":
            self._browser = await self._playwright.chromium.launch(
                headless=headless,
                args=["--disable-dev-shm-usage", "--no-sandbox"]
            )
        return self._browser

    async def create_context(self, session_id: str, viewport: dict = None, user_agent: str = None) -> BrowserContext:
        if not self._browser:
            raise RuntimeError("Browser not started")
            
        vp = viewport or {"width": 1920, "height": 1080}
        return await self._browser.new_context(
            viewport=vp,
            user_agent=user_agent,
            record_video_dir=f"/tmp/videos/{session_id}"
        )

    async def new_page(self, context: BrowserContext) -> Page:
        return await context.new_page()

    async def get_dom_snapshot(self, page: Page) -> dict:
        # Full DOM tree extraction logic would go here
        return {"html": await page.content()}
