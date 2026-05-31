"""
Lightweight httpx + BeautifulSoup scraper for static HTML pages.
Falls back from PlaywrightScraper when JS rendering is not required.
"""

import re
import httpx
from bs4 import BeautifulSoup

from app.modules.scraper.base import ScraperBase, ScrapeResult

_STRIP_TAGS = {"script", "style", "noscript", "head", "meta", "link"}

_HEADERS = {
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(list(_STRIP_TAGS)):
        tag.decompose()
    text = soup.get_text(separator="\n")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class StaticScraper(ScraperBase):
    async def scrape(self, url: str) -> ScrapeResult:
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers=_HEADERS,
            ) as client:
                resp = await client.get(url)
                html = resp.text
                return ScrapeResult(
                    url=url,
                    plain_text=_html_to_text(html),
                    raw_html=html,
                    js_rendered=False,
                    http_status=resp.status_code,
                )
        except Exception as exc:
            return ScrapeResult(
                url=url,
                plain_text="",
                raw_html="",
                js_rendered=False,
                error_message=str(exc),
            )
