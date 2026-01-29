import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import aiofiles

from worker.config import get_settings

settings = get_settings()


class BaseStorageService(ABC):
    """Abstract base class for storage services."""

    @abstractmethod
    async def read_raw_file(self, uri: str) -> bytes:
        pass

    @abstractmethod
    async def save_text_file(self, content: str, candidate_id: str) -> str:
        pass

    @abstractmethod
    async def read_text_file(self, uri: str) -> str:
        pass

    @abstractmethod
    async def save_evidence_file(self, content: str, candidate_id: str) -> str:
        pass


class LocalStorageService(BaseStorageService):
    """Local file storage service."""

    def __init__(self):
        self.base_path = Path(settings.storage_path)
        self.raw_path = self.base_path / "raw"
        self.text_path = self.base_path / "text"
        self.evidence_path = self.base_path / "evidence"

        # Ensure directories exist
        for path in [self.raw_path, self.text_path, self.evidence_path]:
            path.mkdir(parents=True, exist_ok=True)

    async def read_raw_file(self, uri: str) -> bytes:
        """Read a raw file by its URI."""
        filepath = self.base_path / uri
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {uri}")
        async with aiofiles.open(filepath, "rb") as f:
            return await f.read()

    async def save_text_file(self, content: str, candidate_id: str) -> str:
        """Save extracted text and return URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.txt"
        filepath = self.text_path / filename
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(content)
        return f"text/{filename}"

    async def read_text_file(self, uri: str) -> str:
        """Read a text file by its URI."""
        filepath = self.base_path / uri
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {uri}")
        async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
            return await f.read()

    async def save_evidence_file(self, content: str, candidate_id: str) -> str:
        """Save evidence JSON and return URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.json"
        filepath = self.evidence_path / filename
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(content)
        return f"evidence/{filename}"

    def get_full_path(self, uri: str) -> Path:
        """Get full filesystem path for a URI."""
        return self.base_path / uri


class GCSStorageService(BaseStorageService):
    """Google Cloud Storage service."""

    def __init__(self):
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket_name = settings.gcs_bucket
        self.bucket = self.client.bucket(self.bucket_name)

    async def read_raw_file(self, uri: str) -> bytes:
        """Read a raw file by its URI."""
        blob = self.bucket.blob(uri)
        if not blob.exists():
            raise FileNotFoundError(f"File not found: {uri}")
        return blob.download_as_bytes()

    async def save_text_file(self, content: str, candidate_id: str) -> str:
        """Save extracted text and return URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.txt"
        blob_name = f"text/{filename}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type="text/plain; charset=utf-8")
        return blob_name

    async def read_text_file(self, uri: str) -> str:
        """Read a text file by its URI."""
        blob = self.bucket.blob(uri)
        if not blob.exists():
            raise FileNotFoundError(f"File not found: {uri}")
        return blob.download_as_text()

    async def save_evidence_file(self, content: str, candidate_id: str) -> str:
        """Save evidence JSON and return URI."""
        filename = f"{candidate_id}_{uuid.uuid4()}.json"
        blob_name = f"evidence/{filename}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type="application/json")
        return blob_name


# Alias for backwards compatibility
StorageService = LocalStorageService


def get_storage() -> BaseStorageService:
    """Get the appropriate storage service based on environment."""
    if settings.gcs_bucket:
        return GCSStorageService()
    return LocalStorageService()
