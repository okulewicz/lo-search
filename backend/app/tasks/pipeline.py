"""
Celery tasks for async school data pipeline:
  1. sync_schools     – pull from RSPO into DB
  2. scrape_school    – scrape a single school website
  3. extract_profile  – run Ollama extraction on scraped content
  4. run_full_pipeline – orchestrates all of the above
"""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.school import School, ScrapedPage, SchoolProfile
from app.modules.school_discovery.discovery_service import SchoolDiscoveryService
from app.modules.scraper.scraper_factory import SmartScraper
from app.modules.extractor.profile_extractor import ProfileExtractor
import structlog

log = structlog.get_logger(__name__)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(name="tasks.sync_schools", bind=True, max_retries=3)
def sync_schools(self):
    """Pull all Mazovian high schools from RSPO and upsert into DB."""
    async def _inner():
        async with AsyncSessionLocal() as db:
            service = SchoolDiscoveryService(db)
            count = await service.sync_mazovian_highschools()
            return count

    try:
        count = _run(_inner())
        log.info("sync_schools.done", count=count)
        return {"synced": count}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="tasks.scrape_school", bind=True, max_retries=2)
def scrape_school(self, school_id: str):
    """Scrape website for a single school and store the result."""
    async def _inner():
        async with AsyncSessionLocal() as db:
            school = await db.get(School, uuid.UUID(school_id))
            if not school or not school.website_url:
                return {"skipped": True, "reason": "no website"}

            scraper = SmartScraper()
            result = await scraper.scrape(school.website_url)

            page = ScrapedPage(
                school_id=school.id,
                url=result.url,
                raw_html=result.raw_html,
                plain_text=result.plain_text,
                js_rendered=result.js_rendered,
                http_status=result.http_status,
                error_message=result.error_message,
                scraped_at=datetime.utcnow(),
            )
            db.add(page)
            await db.commit()
            await db.refresh(page)
            return {"page_id": str(page.id)}

    try:
        return _run(_inner())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="tasks.extract_profile", bind=True, max_retries=2)
def extract_profile(self, school_id: str):
    """Run Ollama extraction on the most recent scraped page for a school."""
    async def _inner():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ScrapedPage)
                .where(ScrapedPage.school_id == uuid.UUID(school_id))
                .where(ScrapedPage.plain_text.isnot(None))
                .order_by(ScrapedPage.scraped_at.desc())
                .limit(1)
            )
            page = result.scalar_one_or_none()
            if not page or not page.plain_text:
                return {"skipped": True, "reason": "no scraped text"}

            extractor = ProfileExtractor()
            extracted = await extractor.extract(page.plain_text)

            existing = await db.execute(
                select(SchoolProfile).where(
                    SchoolProfile.school_id == uuid.UUID(school_id)
                )
            )
            profile = existing.scalar_one_or_none()
            if profile is None:
                profile = SchoolProfile(school_id=uuid.UUID(school_id))
                db.add(profile)

            profile.class_profiles = extracted.get("class_profiles")
            profile.languages_offered = extracted.get("languages_offered")
            profile.extracurricular_activities = extracted.get("extracurricular_activities")
            profile.notable_achievements = extracted.get("notable_achievements")
            profile.description_summary = extracted.get("description_summary")
            profile.raw_extraction = extracted
            profile.model_used = extracted.get("_model")
            profile.extracted_at = datetime.utcnow()

            await db.commit()
            return {"profile_id": str(profile.id)}

    try:
        return _run(_inner())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="tasks.run_full_pipeline")
def run_full_pipeline():
    """Orchestrate: sync → scrape all → extract all."""
    from celery import chain, group

    async def _get_school_ids():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(School.id).where(School.website_url.isnot(None))
            )
            return [str(r[0]) for r in result.fetchall()]

    school_ids = _run(_get_school_ids())
    workflow = (
        sync_schools.si()
        | group(scrape_school.si(sid) for sid in school_ids)
        | group(extract_profile.si(sid) for sid in school_ids)
    )
    workflow.delay()
    return {"status": "pipeline_started", "schools": len(school_ids)}
