"""Admin endpoints to trigger background pipeline tasks."""

from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.tasks.pipeline import sync_schools, scrape_school, extract_profile, run_full_pipeline

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/sync-schools")
async def trigger_sync():
    task = sync_schools.delay()
    return {"task_id": task.id}


@router.post("/scrape/{school_id}")
async def trigger_scrape(school_id: str):
    task = scrape_school.delay(school_id)
    return {"task_id": task.id}


@router.post("/extract/{school_id}")
async def trigger_extract(school_id: str):
    task = extract_profile.delay(school_id)
    return {"task_id": task.id}


@router.post("/run-pipeline")
async def trigger_pipeline():
    task = run_full_pipeline.delay()
    return {"task_id": task.id}


@router.get("/status/{task_id}")
async def task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
