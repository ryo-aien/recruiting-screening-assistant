from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Worker settings loaded from environment variables."""

    # Database
    database_url: str = "mysql+asyncmy://screening_user:screening_pass@db:3306/screening"

    # OpenAI
    openai_api_key: str = ""

    # Storage
    storage_path: str = "/storage"
    gcs_bucket: str | None = None  # Cloud Storage bucket name for GCP deployment

    # Worker settings
    poll_interval: int = 5  # seconds
    max_retries: int = 3
    batch_size: int = 10

    # LLM settings
    llm_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
