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
    """Map raw Institution API response fields to School model kwargs."""
    street = raw.get("hqAddressStreet")
    building = raw.get("hqAddressBuildingNr")
    premise = raw.get("hqAddressPremiseNr")
    address_street = " ".join(
        [p for p in [street, building, premise] if p]
    ) or None

    website = raw.get("website")
    if website and not website.startswith(("http://", "https://")):
        website = f"https://{website}"

    return {
        "rspo_id": str(raw.get("rspo") or raw.get("id", "")),
        "name": raw.get("name", ""),
        "school_type": (raw.get("type") or {}).get("name"),
        "address_street": address_street,
        "address_city": raw.get("hqAddressPostal"),
        "address_postcode": raw.get("hqAddressZipCode"),
        "voivodeship": "Mazowieckie",
        "county": "Warszawa",
        "municipality": (raw.get("hqAddressLocality") or {}).get("name"),
        "latitude": None,
        "longitude": None,
        "website_url": website,
        "phone": raw.get("telephone"),
        "email": raw.get("email"),
        "is_public": None,
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
