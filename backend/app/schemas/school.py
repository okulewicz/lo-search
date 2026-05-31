import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class SchoolBase(BaseModel):
    name: str
    school_type: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_postcode: Optional[str] = None
    voivodeship: Optional[str] = None
    county: Optional[str] = None
    municipality: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_public: Optional[bool] = None


class SchoolRead(SchoolBase):
    id: uuid.UUID
    rspo_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SchoolProfileRead(BaseModel):
    id: uuid.UUID
    school_id: uuid.UUID
    class_profiles: Optional[dict] = None
    languages_offered: Optional[list] = None
    extracurricular_activities: Optional[list] = None
    notable_achievements: Optional[list] = None
    description_summary: Optional[str] = None
    extracted_at: datetime
    model_used: Optional[str] = None

    model_config = {"from_attributes": True}


class SchoolWithProfile(SchoolRead):
    profile: Optional[SchoolProfileRead] = None


class SchoolListResponse(BaseModel):
    items: list[SchoolRead]
    total: int
    page: int
    size: int
