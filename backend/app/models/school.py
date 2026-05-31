import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Text, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rspo_id: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(512))
    school_type: Mapped[Optional[str]] = mapped_column(String(128))  # e.g. "liceum ogólnokształcące"
    address_street: Mapped[Optional[str]] = mapped_column(String(256))
    address_city: Mapped[Optional[str]] = mapped_column(String(128))
    address_postcode: Mapped[Optional[str]] = mapped_column(String(16))
    voivodeship: Mapped[Optional[str]] = mapped_column(String(64))
    county: Mapped[Optional[str]] = mapped_column(String(128))  # powiat
    municipality: Mapped[Optional[str]] = mapped_column(String(128))  # gmina
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    website_url: Mapped[Optional[str]] = mapped_column(String(512))
    phone: Mapped[Optional[str]] = mapped_column(String(64))
    email: Mapped[Optional[str]] = mapped_column(String(256))
    is_public: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    scraped_pages: Mapped[list["ScrapedPage"]] = relationship(back_populates="school")
    profile: Mapped[Optional["SchoolProfile"]] = relationship(back_populates="school", uselist=False)


class ScrapedPage(Base):
    __tablename__ = "scraped_pages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schools.id"), index=True)
    url: Mapped[str] = mapped_column(String(1024))
    raw_html: Mapped[Optional[str]] = mapped_column(Text)
    plain_text: Mapped[Optional[str]] = mapped_column(Text)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    js_rendered: Mapped[bool] = mapped_column(Boolean, default=False)
    http_status: Mapped[Optional[int]] = mapped_column(Integer)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    school: Mapped["School"] = relationship(back_populates="scraped_pages")


class SchoolProfile(Base):
    """Structured school profile extracted by Ollama from scraped content."""

    __tablename__ = "school_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    school_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("schools.id"), unique=True, index=True
    )
    # Extracted fields (stored as JSONB for flexibility + typed columns for querying)
    class_profiles: Mapped[Optional[dict]] = mapped_column(JSONB)   # e.g. {"mat-fiz": {...}, "hum": {...}}
    languages_offered: Mapped[Optional[list]] = mapped_column(JSONB)
    extracurricular_activities: Mapped[Optional[list]] = mapped_column(JSONB)
    notable_achievements: Mapped[Optional[list]] = mapped_column(JSONB)
    description_summary: Mapped[Optional[str]] = mapped_column(Text)
    raw_extraction: Mapped[Optional[dict]] = mapped_column(JSONB)    # full LLM response
    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    model_used: Mapped[Optional[str]] = mapped_column(String(128))

    school: Mapped["School"] = relationship(back_populates="profile")
