"""
Scraper factory: tries static scraping first; if the result looks JS-only
(very little text, signs of SPA frameworks), falls back to Playwright.
"""

from app.modules.scraper.base import ScraperBase, ScrapeResult
from app.modules.scraper.static_scraper import StaticScraper
from app.modules.scraper.playwright_scraper import PlaywrightScraper

# Heuristic threshold: if fewer than this many words are extracted from
# static HTML we assume the page is JS-driven.
_MIN_WORDS_THRESHOLD = 80


class SmartScraper(ScraperBase):
    """
    Two-stage scraper:
      1. Fast static HTTP fetch.
      2. Playwright full-browser render if static result is too thin.
    """

    def __init__(self) -> None:
        self._static = StaticScraper()
        self._playwright = PlaywrightScraper()

    async def scrape(self, url: str) -> ScrapeResult:
        result = await self._static.scrape(url)

        if self._needs_js_render(result):
            result = await self._playwright.scrape(url)

        return result

    @staticmethod
    def _needs_js_render(result: ScrapeResult) -> bool:
        if result.error_message:
            return True
        word_count = len(result.plain_text.split())
        return word_count < _MIN_WORDS_THRESHOLD
