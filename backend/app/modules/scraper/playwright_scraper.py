"""
Playwright-based scraper for JavaScript-rendered pages.
Uses a headless Chromium browser to fully render the page before extraction.
"""

import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from app.modules.scraper.base import ScraperBase, ScrapeResult


_STRIP_TAGS = {"script", "style", "noscript", "head", "meta", "link"}


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(list(_STRIP_TAGS)):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


class PlaywrightScraper(ScraperBase):
    """Renders page with headless Chromium, waits for network idle."""

    async def scrape(self, url: str) -> ScrapeResult:
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context(
                    locale="pl-PL",
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                )
                page = await context.new_page()
                response = await page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=30_000,
                )
                html = await page.content()
                await browser.close()

            return ScrapeResult(
                url=url,
                plain_text=_html_to_text(html),
                raw_html=html,
                js_rendered=True,
                http_status=response.status if response else None,
            )
        except PlaywrightTimeout as exc:
            return ScrapeResult(
                url=url,
                plain_text="",
                raw_html="",
                js_rendered=True,
                error_message=f"Timeout: {exc}",
            )
        except Exception as exc:
            return ScrapeResult(
                url=url,
                plain_text="",
                raw_html="",
                js_rendered=True,
                error_message=str(exc),
            )
