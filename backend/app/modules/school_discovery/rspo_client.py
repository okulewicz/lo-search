"""
Client for the Polish RSPO (Rejestr Szkół i Placówek Oświatowych) REST API.
Documentation: https://api.rspo.gov.pl
"""

import httpx
from typing import AsyncIterator
from app.config import settings


# School type codes for Warsaw/Mazovia high schools
HIGHSCHOOL_TYPE_CODES = [
    "14",   # Liceum ogólnokształcące
    "17",   # Technikum
    "18",   # Branżowa szkoła I stopnia (vocational)
    "19",   # Branżowa szkoła II stopnia
]

MAZOVIA_VOIVODESHIP_CODE = "14"  # teryt code for Mazowieckie


class RSPOClient:
    """Async client wrapping the RSPO public REST API."""

    def __init__(self) -> None:
        self._base = settings.rspo_api_url.rstrip("/")

    async def fetch_schools_page(
        self,
        page: int = 1,
        page_size: int = 100,
        voivodeship_code: str = MAZOVIA_VOIVODESHIP_CODE,
        school_type_code: str | None = None,
    ) -> dict:
        params: dict = {
            "stronaWynikow": page,
            "iloscWynikow": page_size,
            "kodWojewodztwa": voivodeship_code,
        }
        if school_type_code:
            params["kodTypuSzkoly"] = school_type_code

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{self._base}/placowki", params=params)
            resp.raise_for_status()
            return resp.json()

    async def iter_highschools(
        self, voivodeship_code: str = MAZOVIA_VOIVODESHIP_CODE
    ) -> AsyncIterator[dict]:
        """Yield raw school dicts for all Mazovian high school types."""
        for type_code in HIGHSCHOOL_TYPE_CODES:
            page = 1
            while True:
                data = await self.fetch_schools_page(
                    page=page,
                    voivodeship_code=voivodeship_code,
                    school_type_code=type_code,
                )
                items = data.get("data", [])
                for item in items:
                    yield item
                total_pages = data.get("totalPages", 1)
                if page >= total_pages:
                    break
                page += 1

    async def get_school_details(self, rspo_id: str) -> dict:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{self._base}/placowki/{rspo_id}")
            resp.raise_for_status()
            return resp.json()
