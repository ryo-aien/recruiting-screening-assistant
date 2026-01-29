from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "mysql+asyncmy://screening_user:screening_pass@db:3306/screening"

    # OpenAI
    openai_api_key: str = ""

    # Storage
    storage_path: str = "/storage"
    gcs_bucket: str | None = None  # Cloud Storage bucket name for GCP deployment

    # Application
    debug: bool = False
    environment: str = "production"  # development or production

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
