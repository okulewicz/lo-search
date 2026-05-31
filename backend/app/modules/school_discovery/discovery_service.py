"""
Service that fetches schools from RSPO and upserts them into the database.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.school import School
from app.modules.school_discovery.rspo_client import RSPOClient

log = structlog.get_logger(__name__)


def _map_rspo_to_school(raw: dict) -> dict:
    """Map raw RSPO API response fields to School model kwargs."""
    address = raw.get("adres", {})
    coords = raw.get("geolokalizacja") or {}
    return {
        "rspo_id": str(raw.get("rspo") or raw.get("numerRspo", "")),
        "name": raw.get("nazwa", ""),
        "school_type": raw.get("typSzkoly", {}).get("nazwa"),
        "address_street": address.get("ulica"),
        "address_city": address.get("miejscowosc"),
        "address_postcode": address.get("kodPocztowy"),
        "voivodeship": address.get("wojewodztwo"),
        "county": address.get("powiat"),
        "municipality": address.get("gmina"),
        "latitude": coords.get("szerGeogr"),
        "longitude": coords.get("dlugGeogr"),
        "website_url": raw.get("stronaInternetowa"),
        "phone": raw.get("telefon"),
        "email": raw.get("email"),
        "is_public": raw.get("czyPubliczna"),
    }


class SchoolDiscoveryService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._rspo = RSPOClient()

    async def sync_mazovian_highschools(self) -> int:
        """Pull all Mazovian high schools from RSPO and upsert into DB.
        Returns the number of schools processed."""
        count = 0
        async for raw in self._rspo.iter_highschools():
            await self._upsert_school(raw)
            count += 1
            if count % 50 == 0:
                log.info("school_sync.progress", count=count)
                await self._db.commit()

        await self._db.commit()
        log.info("school_sync.complete", total=count)
        return count

    async def _upsert_school(self, raw: dict) -> School:
        kwargs = _map_rspo_to_school(raw)
        rspo_id = kwargs.get("rspo_id")

        result = await self._db.execute(
            select(School).where(School.rspo_id == rspo_id)
        )
        school = result.scalar_one_or_none()

        if school is None:
            school = School(**kwargs)
            self._db.add(school)
        else:
            for k, v in kwargs.items():
                setattr(school, k, v)

        return school
