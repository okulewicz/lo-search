from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapeResult:
    url: str
    plain_text: str
    raw_html: str
    js_rendered: bool
    http_status: Optional[int] = None
    error_message: Optional[str] = None


class ScraperBase(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> ScrapeResult:
        """Fetch a URL and return its cleaned plain text and raw HTML."""
        ...
