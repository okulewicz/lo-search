from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://losearch:losearch@localhost:5432/losearch"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Transit
    transit_provider: Literal["google_maps", "otp"] = "otp"
    google_maps_api_key: str = ""
    otp_base_url: str = "http://localhost:8080/otp/routers/default"

    # School registry (RSPO)
    rspo_api_url: str = "https://api.rspo.gov.pl/v1"

    # App
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
