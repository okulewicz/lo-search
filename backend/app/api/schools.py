import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.school import School
from app.schemas.school import SchoolRead, SchoolWithProfile, SchoolListResponse

router = APIRouter(prefix="/schools", tags=["schools"])


@router.get("/", response_model=SchoolListResponse)
async def list_schools(
    city: str | None = Query(None),
    county: str | None = Query(None),
    school_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(School)
    if city:
        query = query.where(School.address_city.ilike(f"%{city}%"))
    if county:
        query = query.where(School.county.ilike(f"%{county}%"))
    if school_type:
        query = query.where(School.school_type.ilike(f"%{school_type}%"))

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    items_result = await db.execute(
        query.offset((page - 1) * size).limit(size)
    )
    items = items_result.scalars().all()

    return SchoolListResponse(items=items, total=total, page=page, size=size)


@router.get("/{school_id}", response_model=SchoolWithProfile)
async def get_school(school_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    school = await db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school
