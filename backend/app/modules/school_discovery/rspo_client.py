"""
Client for RSPO Institution API exposed at https://rspo.gov.pl/api/Institution.
This endpoint does not require an API key and supports filter-based POST queries.
"""

import httpx
from typing import AsyncIterator
from app.config import settings


_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://rspo.gov.pl/institutions",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
}


class RSPOClient:
    """Async client wrapping the RSPO Institution API."""

    def __init__(self) -> None:
        self._base = settings.rspo_api_url.rstrip("/")

    async def fetch_schools_page(
        self,
        page_offset: int = 0,
        page_size: int = 100,
    ) -> dict:
        params = {
            "PageOffset": page_offset,
            "PageSize": page_size,
            "IsDescending": "false",
            "OrderBy": "",
        }
        payload = {
            "stateId": settings.rspo_state_id,
            "districtId": settings.rspo_district_id,
            "institutionTypeIdList": settings.rspo_institution_type_ids,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._base}/Institution",
                params=params,
                headers=_REQUEST_HEADERS,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    async def iter_highschools(self, page_size: int = 100) -> AsyncIterator[dict]:
        """Yield Warsaw high schools filtered by configured state/district/type IDs."""
        page_offset = 0
        while True:
            data = await self.fetch_schools_page(
                page_offset=page_offset,
                page_size=page_size,
            )

            items = data.get("items", [])
            for item in items:
                yield item

            total_count = int(data.get("totalCount", 0))
            page_offset += page_size
            if page_offset >= total_count or not items:
                break

    async def get_school_details(self, rspo_id: str) -> dict:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{self._base}/Institution/{rspo_id}")
            resp.raise_for_status()
            return resp.json()
